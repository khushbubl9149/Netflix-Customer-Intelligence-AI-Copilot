import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

# ==========================================
# 1. LOAD DATASET
# ==========================================

df = pd.read_csv("data/ml_customer_dataset.csv")

print("Dataset loaded successfully")
print("Shape:", df.shape)

# ==========================================
# 2. CREATE DATE FEATURES
# ==========================================

df["registration_date"] = pd.to_datetime(
    df["registration_date"],
    errors="coerce"
)

df["registration_year"] = df["registration_date"].dt.year
df["registration_month"] = df["registration_date"].dt.month

# Remove original date column
df.drop(columns=["registration_date"], inplace=True)

# ==========================================
# 3. REMOVE ID
# ==========================================

df.drop(columns=["customer_id"], inplace=True)

# ==========================================
# 4. SEPARATE FEATURES AND TARGET
# ==========================================

X = df.drop(columns=["churn"])
y = df["churn"]

print("\nFeatures:", X.shape)
print("Target:", y.shape)

# ==========================================
# 5. IDENTIFY COLUMNS
# ==========================================

categorical_features = X.select_dtypes(
    include=["object"]
).columns.tolist()

numeric_features = X.select_dtypes(
    include=["int64", "float64"]
).columns.tolist()

print("\nCategorical features:")
print(categorical_features)

print("\nNumeric features:")
print(numeric_features)

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
# 8. COLUMN TRANSFORMER
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

print("\nTrain shape:", X_train.shape)
print("Test shape:", X_test.shape)

print("\nTrain target distribution:")
print(y_train.value_counts())

print("\nTest target distribution:")
print(y_test.value_counts())

# ==========================================
# 10. FIT PREPROCESSOR
# ==========================================

X_train_processed = preprocessor.fit_transform(X_train)
X_test_processed = preprocessor.transform(X_test)

print("\nProcessed train shape:", X_train_processed.shape)
print("Processed test shape:", X_test_processed.shape)

print("\nPreprocessing completed successfully!")