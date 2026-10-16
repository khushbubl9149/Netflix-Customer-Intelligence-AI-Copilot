import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL



# --------------------------------------------------
# 1. Load environment variables
# --------------------------------------------------

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


# --------------------------------------------------
# 2. Create PostgreSQL connection
# --------------------------------------------------

DB_URL = URL.create(
    "postgresql+psycopg2",
    username="postgres",
    password=DB_PASSWORD,      # @ jaise characters yahan chalenge
    host="localhost",
    port=5432,
    database="netflix_customer_intelligence",
)

engine = create_engine(DB_URL)
from sqlalchemy import inspect
print(inspect(engine).get_table_names())


# --------------------------------------------------
# 3. Processed data folder
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_FOLDER = PROJECT_ROOT / "data" / "processed"



# --------------------------------------------------
# 4. CSV → PostgreSQL table mapping
# --------------------------------------------------

FILES = {
    "customers_clean.csv": "customers",
    "subscription_plans_clean.csv": "subscription_plans",
    "subscriptions_clean.csv": "subscriptions",
    "content_clean.csv": "content",
    "viewing_activity_clean.csv": "viewing_activity",
    "payments_clean.csv": "payments",
    "support_tickets_clean.csv": "support_tickets",
    "customer_feedback_clean.csv": "customer_feedback",
    "churn_labels_clean.csv": "churn_labels",
}


# --------------------------------------------------
# 5. Load each CSV
# --------------------------------------------------

for filename, table_name in FILES.items():

    file_path = DATA_FOLDER / filename

    if not file_path.exists():
        print(f"FILE NOT FOUND: {file_path}")
        continue

    print(f"\nLoading {filename}...")

    df = pd.read_csv(file_path)

    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    # chunk = max(1, 60000 // len(df.columns))
    try:
        df.to_sql(


            table_name,
            engine,
            if_exists="append",
            index=False,
            chunksize=1000,
    )

        print(f"Loaded successfully → {table_name}")
    except Exception as e:
        root = e
        while root.__cause__ is not None:
            root = root.__cause__
        
        print("REAL ERROR:", str(root) )

print("\nAll available CSV files processed.")
