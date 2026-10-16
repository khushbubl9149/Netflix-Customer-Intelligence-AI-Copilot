import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")



DB_URL = URL.create(
    "postgresql+psycopg2",
    username="postgres",
    password=DB_PASSWORD,      # @ jaise characters yahan chalenge
    host="localhost",
    port=5432,
    database="netflix_customer_intelligence",
)

engine = create_engine(DB_URL)

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version();"))
        print("PostgreSQL connection successful!")
        print(result.fetchone()[0])

except Exception as e:
    print("Connection failed:")
    print(e)