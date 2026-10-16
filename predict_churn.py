import sys
import pandas as pd
import joblib


# ========================================
# CONFIGURATION
# ========================================

MODEL_PATH = "models/churn_random_forest.pkl"
PREPROCESSOR_PATH = "models/churn_preprocessor.pkl"

CHURN_THRESHOLD = 0.40


# ========================================
# GET CUSTOMER ID
# ========================================

if len(sys.argv) < 2:

    print("\nUsage:")
    print(
        "python src\\ml\\predict_churn.py CUSTOMER_ID"
    )

    print("\nExample:")
    print(
        "python src\\ml\\predict_churn.py CUST000001"
    )

    sys.exit()


customer_id = sys.argv[1]


# ========================================
# LOAD MODEL
# ========================================

model = joblib.load(
    MODEL_PATH
)

preprocessor = joblib.load(
    PREPROCESSOR_PATH
)


print(
    "Model loaded successfully!"
)


# ========================================
# LOAD DATA
# ========================================

df = pd.read_csv(
    "data/ml_customer_dataset.csv"
)


# ========================================
# FIND CUSTOMER
# ========================================

customer = df[
    df["customer_id"] == customer_id
].copy()


if customer.empty:

    print(
        f"\nCustomer {customer_id} not found."
    )

    sys.exit()


# ========================================
# PREPARE FEATURES
# ========================================

customer["registration_date"] = (
    pd.to_datetime(
        customer["registration_date"]
    )
)

customer["registration_year"] = (
    customer["registration_date"].dt.year
)

customer["registration_month"] = (
    customer["registration_date"].dt.month
)


customer.drop(
    columns=[
        "registration_date",
        "customer_id",
        "churn"
    ],
    inplace=True
)


# ========================================
# PREPROCESS
# ========================================

customer_processed = (
    preprocessor.transform(
        customer
    )
)


# ========================================
# PREDICT
# ========================================

churn_probability = (
    model.predict_proba(
        customer_processed
    )[0][1]
)


prediction = int(
    churn_probability >= CHURN_THRESHOLD
)


# ========================================
# RISK LEVEL
# ========================================

if churn_probability >= 0.70:

    risk_level = "Very High"

elif churn_probability >= 0.50:

    risk_level = "High"

elif churn_probability >= 0.40:

    risk_level = "Medium"

else:

    risk_level = "Low"


# ========================================
# RESULT
# ========================================

print("\n========================================")
print("CUSTOMER CHURN PREDICTION")
print("========================================")

print(
    f"Customer ID       : {customer_id}"
)

print(
    f"Churn Probability : "
    f"{churn_probability:.2%}"
)

print(
    f"Threshold         : "
    f"{CHURN_THRESHOLD:.2f}"
)

print(
    "Prediction        : "
    + (
        "LIKELY TO CHURN"
        if prediction == 1
        else "NOT LIKELY TO CHURN"
    )
)

print(
    f"Risk Level        : {risk_level}"
)

print("========================================")