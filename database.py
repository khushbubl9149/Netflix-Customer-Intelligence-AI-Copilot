import os
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus


# ==========================================
# DATABASE CONFIGURATION
# ==========================================

DB_USER = "postgres"
DB_PASSWORD = "Bhavya@2912"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "netflix_customer_intelligence"


# ==========================================
# DATABASE CONNECTION
# ==========================================

encoded_password = quote_plus(DB_PASSWORD)

DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{DB_USER}:{encoded_password}@"
    f"{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)


# ==========================================
# TEST DATABASE CONNECTION
# ==========================================

def test_connection():

    try:

        with engine.connect() as connection:

            result = connection.execute(
                text("SELECT 1")
            )

            result.fetchone()

        print("PostgreSQL connection successful!")

    except Exception as e:

        print("Database connection failed!")
        print(e)


if __name__ == "__main__":

    test_connection()