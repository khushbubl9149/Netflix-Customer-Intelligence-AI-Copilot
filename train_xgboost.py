import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report,
    confusion_matrix
)

from xgboost import XGBClassifier


# ========================================
# 1. LOAD DATA
# ========================================

df = pd.read_csv("data/ml_customer_dataset.csv")

print("Dataset loaded:", df.shape)


# ========================================
# 2. FEATURE ENGINEERING
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
    columns=["registration_date", "customer_id"],
    inplace=True
)


# ========================================
# 3. X AND Y
# ========================================

X = df.drop(columns=["churn"])
y = df["churn"]


# ========================================
# 4. IDENTIFY FEATURES
# ========================================

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


# ========================================
# 5. PREPROCESSING
# ========================================

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


categorical_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(strategy="most_frequent")
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
# 7. PREPROCESS
# ========================================

X_train_processed = preprocessor.fit_transform(
    X_train
)

X_test_processed = preprocessor.transform(
    X_test
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
# 8. XGBOOST MODEL
# ========================================

print("\nTraining XGBoost...")

xgb_model = XGBClassifier(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    
    subsample=0.8,
    colsample_bytree=0.8,
    min_child_weight=3,
    gamma=0,
    reg_alpha=0,
    reg_lambda=1,
    scale_pos_weight=3.02,
    objective="binary:logistic",
    eval_metric="logloss",
    random_state=42,
    n_jobs=-1
)


xgb_model.fit(
    X_train_processed,
    y_train
)

print("XGBoost training completed!")


# ========================================
# 9. PREDICTIONS
# ========================================

y_pred = xgb_model.predict(
    X_test_processed
)

y_probability = xgb_model.predict_proba(
    X_test_processed
)[:, 1]


# ========================================
# 10. PERFORMANCE
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
print("XGBOOST MODEL PERFORMANCE")
print("========================================")

print(f"Accuracy  : {accuracy:.4f}")
print(f"Precision : {precision:.4f}")
print(f"Recall    : {recall:.4f}")
print(f"F1 Score  : {f1:.4f}")
print(f"ROC-AUC   : {roc_auc:.4f}")


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
    xgb_model,
    "models/churn_xgboost.pkl"
)

joblib.dump(
    preprocessor,
    "models/xgb_preprocessor.pkl"
)


print("\n========================================")
print("FILES SAVED")
print("========================================")

print("models/churn_xgboost.pkl")
print("models/xgb_preprocessor.pkl")