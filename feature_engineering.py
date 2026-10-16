import pandas as pd
import numpy as np


# ========================================
# 1. LOAD DATA
# ========================================

df = pd.read_csv("data/ml_customer_dataset.csv")

print("Original dataset:", df.shape)


# ========================================
# 2. DATE FEATURES
# ========================================

df["registration_date"] = pd.to_datetime(
    df["registration_date"]
)

df["registration_year"] = (
    df["registration_date"].dt.year
)

df["registration_month"] = (
    df["registration_date"].dt.month
)


# ========================================
# 3. PAYMENT FEATURES
# ========================================

# Failed payment rate
df["failed_payment_rate"] = np.where(
    df["total_payments"] > 0,
    df["failed_payments"] / df["total_payments"],
    0
)


# Average payment amount
df["average_payment_amount"] = np.where(
    df["total_payments"] > 0,
    df["total_payment_amount"] / df["total_payments"],
    0
)


# ========================================
# 4. VIEWING / ENGAGEMENT FEATURES
# ========================================

# Average watch time per session
df["avg_watch_minutes_per_session"] = np.where(
    df["total_sessions"] > 0,
    df["total_watch_minutes"] / df["total_sessions"],
    0
)


# Average watch time per payment
df["watch_minutes_per_payment"] = np.where(
    df["total_payments"] > 0,
    df["total_watch_minutes"] / df["total_payments"],
    0
)


# Sessions per payment
df["sessions_per_payment"] = np.where(
    df["total_payments"] > 0,
    df["total_sessions"] / df["total_payments"],
    0
)


# ========================================
# 5. SUPPORT FEATURES
# ========================================

# Support tickets per payment
df["support_tickets_per_payment"] = np.where(
    df["total_payments"] > 0,
    df["total_support_tickets"] / df["total_payments"],
    0
)


# Support tickets per session
df["support_tickets_per_session"] = np.where(
    df["total_sessions"] > 0,
    df["total_support_tickets"] / df["total_sessions"],
    0
)


# ========================================
# 6. CUSTOMER ENGAGEMENT SCORE
# ========================================

df["engagement_score"] = (
    df["avg_completion_percentage"] * 0.40
    + df["total_sessions"] * 0.20
    + df["avg_watch_minutes_per_session"] * 0.40
)


# ========================================
# 7. PAYMENT RELIABILITY SCORE
# ========================================

df["payment_reliability_score"] = (
    1 - df["failed_payment_rate"]
) * 100


# ========================================
# 8. CUSTOMER ACTIVITY FEATURES
# ========================================

df["feedback_per_session"] = np.where(
    df["total_sessions"] > 0,
    df["total_feedback"] / df["total_sessions"],
    0
)


df["tickets_per_100_sessions"] = np.where(
    df["total_sessions"] > 0,
    (df["total_support_tickets"] / df["total_sessions"]) * 100,
    0
)


# ========================================
# 9. TENURE GROUP
# ========================================

df["tenure_group"] = pd.cut(
    df["tenure_days"],
    bins=[
        -1,
        90,
        180,
        365,
        730,
        float("inf")
    ],
    labels=[
        "0-3 Months",
        "3-6 Months",
        "6-12 Months",
        "1-2 Years",
        "2+ Years"
    ]
)


# ========================================
# 10. ENGAGEMENT CATEGORY
# ========================================

df["engagement_category"] = pd.cut(
    df["avg_completion_percentage"],
    bins=[
        -1,
        40,
        60,
        80,
        100
    ],
    labels=[
        "Low",
        "Medium",
        "High",
        "Very High"
    ]
)


# ========================================
# 11. PAYMENT RISK CATEGORY
# ========================================

df["payment_risk_category"] = pd.cut(
    df["failed_payment_rate"],
    bins=[
        -0.001,
        0,
        0.10,
        0.25,
        1
    ],
    labels=[
        "No Failed Payments",
        "Low Risk",
        "Medium Risk",
        "High Risk"
    ]
)


# ========================================
# 12. REMOVE CUSTOMER ID
# ========================================

# Keep customer_id temporarily for validation
customer_ids = df["customer_id"].copy()


# ========================================
# 13. SAVE FEATURE-ENGINEERED DATASET
# ========================================

df.to_csv(
    "data/ml_customer_features.csv",
    index=False
)


# ========================================
# 14. VALIDATION
# ========================================

print("\n========================================")
print("FEATURE ENGINEERING COMPLETED")
print("========================================")

print("Original shape:", (len(df), 20))
print("New shape:", df.shape)

print("\nNew Features:")

new_features = [
    "failed_payment_rate",
    "average_payment_amount",
    "avg_watch_minutes_per_session",
    "watch_minutes_per_payment",
    "sessions_per_payment",
    "support_tickets_per_payment",
    "support_tickets_per_session",
    "engagement_score",
    "payment_reliability_score",
    "feedback_per_session",
    "tickets_per_100_sessions"
]

for feature in new_features:
    print("-", feature)


print("\nMissing values:")

print(
    df[new_features].isnull().sum()
)


print("\nFeature-engineered dataset saved to:")

print("data/ml_customer_features.csv")