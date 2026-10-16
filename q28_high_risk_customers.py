
import pandas as pd
import joblib

from sqlalchemy import text
from src.copilot.sql_engine import engine

MODEL_PATH = "models/churn_random_forest.pkl"
PREPROCESSOR_PATH = "models/churn_preprocessor.pkl"
DATA_PATH = "data/ml_customer_dataset.csv"

CHURN_THRESHOLD = 0.40

# Step 1: Find customers meeting Q28's SQL conditions
query = """
    SELECT
        p.customer_id,
        COUNT(*) AS failed_payment_count,
        sp.plan_name AS current_plan
    FROM payments p
    JOIN subscriptions s
        ON p.subscription_id = s.subscription_id
    JOIN subscription_plans sp
        ON s.plan_id = sp.plan_id
    WHERE LOWER(TRIM(p.payment_status)) = 'failed'
      AND p.payment_date >= CURRENT_DATE - INTERVAL '90 days'
      AND p.payment_date < CURRENT_DATE + INTERVAL '1 day'
      AND LOWER(TRIM(s.subscription_status)) = 'active'
    GROUP BY p.customer_id, sp.plan_name
    HAVING COUNT(*) >= 2
    ORDER BY failed_payment_count DESC
"""

with engine.connect() as connection:
    candidates = pd.DataFrame(
        connection.execute(text(query)).mappings().all()
    )

if candidates.empty:
    print("Q28 result: No customers meet the failed-payment criteria.")
    print("The payment dataset currently ends on 2026-05-31.")
    raise SystemExit(0)

# Step 2: Load model and customer features
model = joblib.load(MODEL_PATH)
preprocessor = joblib.load(PREPROCESSOR_PATH)
df = pd.read_csv(DATA_PATH)

# Step 3: Match eligible customers to model dataset
eligible = candidates.merge(
    df,
    on="customer_id",
    how="inner"
)

if eligible.empty:
    print("No SQL-qualified customers were found in the ML dataset.")
    raise SystemExit(0)

# Step 4: Prepare features in the same way as predict_churn.py
features = eligible.drop(
    columns=["customer_id", "churn"],
    errors="ignore"
).copy()

features["registration_date"] = pd.to_datetime(
    features["registration_date"]
)
features["registration_year"] = features["registration_date"].dt.year
features["registration_month"] = features["registration_date"].dt.month

features.drop(columns=["registration_date"], inplace=True)

# Step 5: Predict risk
processed = preprocessor.transform(features)
probabilities = model.predict_proba(processed)[:, 1]

eligible["churn_probability"] = probabilities
eligible["risk_level"] = eligible["churn_probability"].apply(
    lambda p: (
        "Very High" if p >= 0.70 else
        "High" if p >= 0.50 else
        "Medium" if p >= CHURN_THRESHOLD else
        "Low"
    )
)

# Step 6: Keep only High and Very High risk
result = eligible[
    eligible["risk_level"].isin(["High", "Very High"])
][[
    "customer_id",
    "failed_payment_count",
    "current_plan",
    "churn_probability",
    "risk_level"
]].sort_values(
    ["churn_probability", "failed_payment_count"],
    ascending=[False, False]
)

print("\n========== Q28 HIGH CHURN-RISK CUSTOMERS ==========")
print(result.to_string(index=False) if not result.empty else
      "No customers met both the SQL and ML risk criteria.")
