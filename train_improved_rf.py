import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
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


# ========================================
# 1. LOAD FEATURE-ENGINEERED DATA
# ========================================

df = pd.read_csv(
    "data/ml_customer_features.csv"
)

print("Dataset loaded:", df.shape)


# ========================================
# 2. REMOVE UNUSED COLUMNS
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

df.drop(
    columns=[
        "registration_date",
        "customer_id"
    ],
    inplace=True
)


# ========================================
# 3. X AND Y
# ========================================

X = df.drop(
    columns=["churn"]
)

y = df["churn"]


# ========================================
# 4. FEATURE TYPES
# ========================================

categorical_features = [
    "gender",
    "country",
    "acquisition_channel",
    "customer_segment",
    "preferred_language",
    "tenure_group",
    "engagement_category",
    "payment_risk_category"
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
    "registration_month",

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


# ========================================
# 5. PREPROCESSING
# ========================================

numeric_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(
                strategy="median"
            )
        ),
        (
            "scaler",
            StandardScaler()
        )
    ]
)


categorical_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(
                strategy="most_frequent"
            )
        ),
        (
            "encoder",
            OneHotEncoder(
                handle_unknown="ignore",
                sparse_output=False
            )
        )
    ]
)


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


# ========================================
# 6. TRAIN TEST SPLIT
# ========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


# ========================================
# 7. PREPROCESS DATA
# ========================================

X_train_processed = (
    preprocessor.fit_transform(X_train)
)

X_test_processed = (
    preprocessor.transform(X_test)
)


print(
    "Processed train:",
    X_train_processed.shape
)

print(
    "Processed test:",
    X_test_processed.shape
)


# ========================================
# 8. RANDOM FOREST
# ========================================

print("\nTraining Improved Random Forest...")


model = RandomForestClassifier(
    n_estimators=500,
    max_depth=14,
    min_samples_split=8,
    min_samples_leaf=3,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)


model.fit(
    X_train_processed,
    y_train
)


print(
    "Improved Random Forest training completed!"
)


# ========================================
# 9. PREDICTIONS
# ========================================

y_pred = model.predict(
    X_test_processed
)

y_probability = model.predict_proba(
    X_test_processed
)[:, 1]


# ========================================
# 10. METRICS
# ========================================

accuracy = accuracy_score(
    y_test,
    y_pred
)

precision = precision_score(
    y_test,
    y_pred
)

recall = recall_score(
    y_test,
    y_pred
)

f1 = f1_score(
    y_test,
    y_pred
)

roc_auc = roc_auc_score(
    y_test,
    y_probability
)


print("\n========================================")
print("IMPROVED RANDOM FOREST PERFORMANCE")
print("========================================")

print(
    f"Accuracy  : {accuracy:.4f}"
)

print(
    f"Precision : {precision:.4f}"
)

print(
    f"Recall    : {recall:.4f}"
)

print(
    f"F1 Score  : {f1:.4f}"
)

print(
    f"ROC-AUC   : {roc_auc:.4f}"
)


# ========================================
# 11. CLASSIFICATION REPORT
# ========================================

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        y_pred,
        target_names=[
            "Not Churned",
            "Churned"
        ]
    )
)


# ========================================
# 12. CONFUSION MATRIX
# ========================================

print("\nConfusion Matrix:")

print(
    confusion_matrix(
        y_test,
        y_pred
    )
)


# ========================================
# 13. SAVE MODEL
# ========================================

joblib.dump(
    model,
    "models/churn_improved_random_forest.pkl"
)

joblib.dump(
    preprocessor,
    "models/improved_rf_preprocessor.pkl"
)


print("\n========================================")
print("FILES SAVED")
print("========================================")

print(
    "models/churn_improved_random_forest.pkl"
)

print(
    "models/improved_rf_preprocessor.pkl"
)