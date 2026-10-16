import sys
import pandas as pd
import joblib


# ==============================
# CONFIGURATION
# ==============================

MODEL_PATH = "models/churn_random_forest.pkl"
PREPROCESSOR_PATH = "models/churn_preprocessor.pkl"
DATA_PATH = "data/ml_customer_dataset.csv"

CHURN_THRESHOLD = 0.40


# ==============================
# LOAD MODEL
# ==============================

model = joblib.load(MODEL_PATH)
preprocessor = joblib.load(PREPROCESSOR_PATH)

print("AI Copilot ML engine loaded successfully!")


# ==============================
# LOAD CUSTOMER DATA
# ==============================

df = pd.read_csv(DATA_PATH)

df["registration_date"] = pd.to_datetime(df["registration_date"])

df["registration_year"] = df["registration_date"].dt.year
df["registration_month"] = df["registration_date"].dt.month


# ==============================
# CUSTOMER CHURN PREDICTION
# ==============================

def predict_customer_churn(customer_id):

    customer = df[df["customer_id"] == customer_id].copy()

    if customer.empty:
        return None

    customer_features = customer.copy()

    customer_features.drop(
        columns=[
            "registration_date",
            "customer_id",
            "churn"
        ],
        inplace=True
    )

    customer_processed = preprocessor.transform(customer_features)

    probability = model.predict_proba(
        customer_processed
    )[0][1]

    prediction = probability >= CHURN_THRESHOLD

    if probability >= 0.70:
        risk_level = "Very High"
    elif probability >= 0.50:
        risk_level = "High"
    elif probability >= 0.40:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    return {
        "customer_id": customer_id,
        "churn_probability": probability,
        "prediction": prediction,
        "risk_level": risk_level
    }


# ==============================
# COPILOT COMMAND LINE
# ==============================
def explain_customer_risk(customer_id):
    customer = df[df["customer_id"].str.upper() == customer_id.upper()]

    if customer.empty:
        return []

    customer = customer.iloc[0]

    reasons = []

    if customer["total_watch_minutes"] < 500:
        reasons.append(
            "Low watch activity indicates weak customer engagement."
        )

    if customer["avg_completion_percentage"] < 60:
        reasons.append(
            "Low average content completion suggests reduced content engagement."
        )

    if customer["failed_payments"] > 0:
        reasons.append(
            f"The customer has {int(customer['failed_payments'])} failed payment(s)."
        )

    if customer["total_support_tickets"] >= 3:
        reasons.append(
            f"The customer has raised {int(customer['total_support_tickets'])} support tickets."
        )

    if customer["avg_support_satisfaction"] < 3:
        reasons.append(
            "Low support satisfaction indicates a poor support experience."
        )

    if customer["avg_rating"] < 3:
        reasons.append(
            "Low average rating indicates customer dissatisfaction."
        )

    if not reasons:
        reasons.append(
            "No single major risk signal was identified; the model is combining multiple customer-level features."
        )

    return reasons


def recommend_retention_actions(customer_id):
    customer = df[df["customer_id"].str.upper() == customer_id.upper()]

    if customer.empty:
        return []

    customer = customer.iloc[0]

    recommendations = []

    if customer["failed_payments"] > 0:
        recommendations.append(
            "Review and resolve the customer's payment issues."
        )

    if customer["total_watch_minutes"] < 500:
        recommendations.append(
            "Send personalized content recommendations to increase engagement."
        )

    if customer["avg_completion_percentage"] < 60:
        recommendations.append(
            "Recommend shorter or more relevant content to improve completion."
        )

    if customer["total_support_tickets"] >= 3:
        recommendations.append(
            "Ask the support team to follow up with the customer."
        )

    if customer["avg_support_satisfaction"] < 3:
        recommendations.append(
            "Review previous support interactions and improve the customer experience."
        )

    if customer["avg_rating"] < 3:
        recommendations.append(
            "Collect feedback and investigate the reasons for dissatisfaction."
        )

    if not recommendations:
        recommendations.append(
            "Monitor the customer and use personalized engagement campaigns."
        )

    return recommendations
# ==========================================
# COMMAND LINE CUSTOMER PREDICTION
# ==========================================

def main():

    if len(sys.argv) < 2:

        print("\nUsage:")
        print("python src\\copilot\\copilot.py CUSTOMER_ID")
        print("\nExample:")
        print("python src\\copilot\\copilot.py CUST002668")
        return

    customer_id = sys.argv[1]

    result = predict_customer_churn(customer_id)

    if result is None:

        print(
            f"\nCustomer {customer_id} not found."
        )
        return

    print("\n========================================")
    print("AI CUSTOMER INTELLIGENCE COPILOT")
    print("========================================")

    print(
        f"Customer ID       : {customer_id}"
    )

    print(
        f"Churn Probability : "
        f"{result['churn_probability']:.2%}"
    )

    print(
        f"Threshold         : {CHURN_THRESHOLD:.2f}"
    )

    print(
        "Prediction        : "
        + (
            "LIKELY TO CHURN"
            if result["prediction"]
            else "NOT LIKELY TO CHURN"
        )
    )

    print(
        f"Risk Level        : {result['risk_level']}"
    )

    print("========================================")


# Only run command-line mode when this file
# is executed directly.
# Do NOT run it when imported by question_router.py.

if __name__ == "__main__":
    main()