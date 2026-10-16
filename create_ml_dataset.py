import os
import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus

# ==============================
# DATABASE CONFIGURATION
# ==============================

DB_USER = "postgres"
DB_PASSWORD = "Bhavya@2912"
encoded_password = quote_plus(DB_PASSWORD)
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "netflix_customer_intelligence"

# Replace YOUR_POSTGRES_PASSWORD with your actual PostgreSQL password.

engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
# ==============================
# SQL QUERY
# ==============================

query = """
WITH customer_features AS (

    SELECT
        c.customer_id,
        c.age,
        c.gender,
        c.country,
        c.acquisition_channel,
        c.customer_segment,
        c.preferred_language,
        c.registration_date,

        -- Tenure
        (
            (SELECT MAX(viewing_date) FROM viewing_activity)
            - c.registration_date
        ) AS tenure_days,

        -- Total viewing activity
        COALESCE(v.total_watch_minutes, 0) AS total_watch_minutes,
        COALESCE(v.total_sessions, 0) AS total_sessions,
        COALESCE(v.avg_completion_percentage, 0) AS avg_completion_percentage,

        -- Payments
        COALESCE(p.total_payments, 0) AS total_payments,
        COALESCE(p.total_payment_amount, 0) AS total_payment_amount,
        COALESCE(p.failed_payments, 0) AS failed_payments,

        -- Support
        COALESCE(s.total_tickets, 0) AS total_support_tickets,
        COALESCE(s.avg_satisfaction_score, 0) AS avg_support_satisfaction,

        -- Feedback
        COALESCE(f.total_feedback, 0) AS total_feedback,
        COALESCE(f.avg_rating, 0) AS avg_rating,

        -- Churn label
        CASE
            WHEN cl.churned = TRUE THEN 1
            ELSE 0
        END AS churn

    FROM customers c

    LEFT JOIN (
        SELECT
            customer_id,
            SUM(watch_duration_minutes) AS total_watch_minutes,
            COUNT(*) AS total_sessions,
            AVG(completion_percentage) AS avg_completion_percentage
        FROM viewing_activity
        GROUP BY customer_id
    ) v
        ON c.customer_id = v.customer_id

    LEFT JOIN (
        SELECT
            customer_id,
            COUNT(*) AS total_payments,
            SUM(
                CASE
                    WHEN LOWER(TRIM(payment_status))
                    IN ('success', 'successful', 'paid', 'completed')
                    THEN amount
                    ELSE 0
                END
            ) AS total_payment_amount,
            COUNT(*) FILTER (
                WHERE LOWER(TRIM(payment_status))
                IN ('failed', 'failure', 'declined', 'rejected')
            ) AS failed_payments
        FROM payments
        GROUP BY customer_id
    ) p
        ON c.customer_id = p.customer_id

    LEFT JOIN (
        SELECT
            customer_id,
            COUNT(*) AS total_tickets,
            AVG(customer_satisfaction_score) AS avg_satisfaction_score
        FROM support_tickets
        GROUP BY customer_id
    ) s
        ON c.customer_id = s.customer_id

    LEFT JOIN (
        SELECT
            customer_id,
            COUNT(*) AS total_feedback,
            AVG(rating) AS avg_rating
        FROM customer_feedback
        GROUP BY customer_id
    ) f
        ON c.customer_id = f.customer_id

    LEFT JOIN churn_labels cl
        ON c.customer_id = cl.customer_id
)

SELECT *
FROM customer_features
ORDER BY customer_id;
"""

# ==============================
# LOAD DATA
# ==============================

print("Connecting to PostgreSQL...")

df = pd.read_sql(query, engine)

print("Dataset created successfully!")
print(f"Rows: {df.shape[0]}")
print(f"Columns: {df.shape[1]}")

# ==============================
# CREATE DATA DIRECTORY
# ==============================

os.makedirs("data", exist_ok=True)

# ==============================
# SAVE DATASET
# ==============================

output_path = "data/ml_customer_dataset.csv"

df.to_csv(output_path, index=False)

print(f"\nDataset saved to: {output_path}")

# ==============================
# BASIC INFORMATION
# ==============================

print("\nDataset Preview:")
print(df.head())

print("\nMissing Values:")
print(df.isnull().sum())

print("\nChurn Distribution:")
print(df["churn"].value_counts())

print("\nChurn Percentage:")
print(df["churn"].value_counts(normalize=True) * 100)