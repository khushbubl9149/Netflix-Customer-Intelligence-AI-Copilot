import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report,
    confusion_matrix
)

import joblib


# ==========================================
# 1. LOAD DATA
# ==========================================

df = pd.read_csv("data/ml_customer_dataset.csv")

print("Dataset loaded:", df.shape)


# ==========================================
# 2. DATE FEATURES
# ==========================================

df["registration_date"] = pd.to_datetime(
    df["registration_date"],
    errors="coerce"
)

df["registration_year"] = df["registration_date"].dt.year
df["registration_month"] = df["registration_date"].dt.month

df.drop(columns=["registration_date"], inplace=True)


# ==========================================
# 3. REMOVE CUSTOMER ID
# ==========================================

df.drop(columns=["customer_id"], inplace=True)


# ==========================================
# 4. FEATURES AND TARGET
# ==========================================

X = df.drop(columns=["churn"])
y = df["churn"]


# ==========================================
# 5. COLUMN TYPES
# ==========================================

categorical_features = [
    "gender",
    "country",
    "acquisition_channel",
    "customer_segment",
    "preferred_language"
]

numeric_features = [
    "age",
    "tenure_days",
    "total_watch_minutes",
    "total_sessions",
    "avg_completion_percentage",
    "total_payments",
    "total_payment_amount",
    "failed_payments",
    "total_support_tickets",
    "avg_support_satisfaction",
    "total_feedback",
    "avg_rating",
    "registration_year",
    "registration_month"
]


# ==========================================
# 6. NUMERIC PIPELINE
# ==========================================

numeric_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(strategy="median")
        ),
        (
            "scaler",
            StandardScaler()
        )
    ]
)


# ==========================================
# 7. CATEGORICAL PIPELINE
# ==========================================

categorical_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(strategy="most_frequent")
        ),
        (
            "onehot",
            OneHotEncoder(
                handle_unknown="ignore",
                sparse_output=False
            )
        )
    ]
)


# ==========================================
# 8. PREPROCESSOR
# ==========================================

preprocessor = ColumnTransformer(
    transformers=[
        (
            "numeric",
            numeric_pipeline,
            numeric_features
        ),
        (
            "categorical",
            categorical_pipeline,
            categorical_features
        )
    ]
)


# ==========================================
# 9. TRAIN / TEST SPLIT
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


# ==========================================
# 10. PREPROCESS DATA
# ==========================================

X_train_processed = preprocessor.fit_transform(X_train)
X_test_processed = preprocessor.transform(X_test)


print("\nProcessed train:", X_train_processed.shape)
print("Processed test:", X_test_processed.shape)


# ==========================================
# 11. RANDOM FOREST MODEL
# ==========================================

model = RandomForestClassifier(
    n_estimators=300,
    max_depth=12,
    min_samples_split=10,
    min_samples_leaf=4,
    random_state=42,
    class_weight="balanced",
    n_jobs=-1
)


print("\nTraining Random Forest...")

model.fit(
    X_train_processed,
    y_train
)

print("Model training completed!")


# ==========================================
# 12. PREDICTIONS
# ==========================================

y_pred = model.predict(X_test_processed)

y_probability = model.predict_proba(
    X_test_processed
)[:, 1]


# ==========================================
# 13. MODEL EVALUATION
# ==========================================

accuracy = accuracy_score(y_test, y_pred)

precision = precision_score(
    y_test,
    y_pred,
    zero_division=0
)

recall = recall_score(
    y_test,
    y_pred,
    zero_division=0
)

f1 = f1_score(
    y_test,
    y_pred,
    zero_division=0
)

roc_auc = roc_auc_score(
    y_test,
    y_probability
)


print("\n========================================")
print("RANDOM FOREST MODEL PERFORMANCE")
print("========================================")

print(f"Accuracy  : {accuracy:.4f}")
print(f"Precision : {precision:.4f}")
print(f"Recall    : {recall:.4f}")
print(f"F1 Score  : {f1:.4f}")
print(f"ROC-AUC   : {roc_auc:.4f}")


# ==========================================
# 14. CLASSIFICATION REPORT
# ==========================================

print("\nClassification Report:")
print(
    classification_report(
        y_test,
        y_pred,
        target_names=[
            "Not Churned",
            "Churned"
        ],
        zero_division=0
    )
)


# ==========================================
# 15. CONFUSION MATRIX
# ==========================================

print("\nConfusion Matrix:")

cm = confusion_matrix(
    y_test,
    y_pred
)

print(cm)


# ==========================================
# 16. SAVE MODEL + PREPROCESSOR
# ==========================================

import os

os.makedirs("models", exist_ok=True)

joblib.dump(
    model,
    "models/churn_random_forest.pkl"
)

joblib.dump(
    preprocessor,
    "models/churn_preprocessor.pkl"
)

print("\n========================================")
print("FILES SAVED")
print("========================================")

print("models/churn_random_forest.pkl")
print("models/churn_preprocessor.pkl")