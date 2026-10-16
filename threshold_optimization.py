import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    accuracy_score,
    roc_auc_score
)


# ========================================
# 1. LOAD DATA
# ========================================

df = pd.read_csv(
    "data/ml_customer_dataset.csv"
)

print("Dataset loaded:", df.shape)


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
# 8. TRAIN RANDOM FOREST
# ========================================

print("\nTraining Random Forest...")


model = RandomForestClassifier(
    n_estimators=300,
    max_depth=12,
    min_samples_split=10,
    min_samples_leaf=4,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)


model.fit(
    X_train_processed,
    y_train
)


print("Training completed!")


# ========================================
# 9. CHURN PROBABILITY
# ========================================

y_probability = model.predict_proba(
    X_test_processed
)[:, 1]


roc_auc = roc_auc_score(
    y_test,
    y_probability
)


print("\n========================================")
print("THRESHOLD OPTIMIZATION")
print("========================================")

print(
    f"ROC-AUC: {roc_auc:.4f}"
)


# ========================================
# 10. TEST DIFFERENT THRESHOLDS
# ========================================

thresholds = [
    0.20,
    0.25,
    0.30,
    0.35,
    0.40,
    0.45,
    0.50,
    0.55,
    0.60
]


results = []


for threshold in thresholds:

    y_pred_threshold = (
        y_probability >= threshold
    ).astype(int)

    accuracy = accuracy_score(
        y_test,
        y_pred_threshold
    )

    precision = precision_score(
        y_test,
        y_pred_threshold,
        zero_division=0
    )

    recall = recall_score(
        y_test,
        y_pred_threshold,
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        y_pred_threshold,
        zero_division=0
    )

    results.append({
        "threshold": threshold,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1
    })


# ========================================
# 11. DISPLAY RESULTS
# ========================================

results_df = pd.DataFrame(
    results
)


print(
    results_df.to_string(
        index=False
    )
)


# ========================================
# 12. BEST F1 THRESHOLD
# ========================================

best_row = results_df.loc[
    results_df["f1"].idxmax()
]


print("\n========================================")
print("BEST THRESHOLD")
print("========================================")

print(
    f"Threshold : {best_row['threshold']:.2f}"
)

print(
    f"Accuracy  : {best_row['accuracy']:.4f}"
)

print(
    f"Precision : {best_row['precision']:.4f}"
)

print(
    f"Recall    : {best_row['recall']:.4f}"
)

print(
    f"F1 Score  : {best_row['f1']:.4f}"
)


# ========================================
# 13. SAVE RESULTS
# ========================================

results_df.to_csv(
    "data/threshold_results.csv",
    index=False
)


print("\nResults saved to:")
print("data/threshold_results.csv")