import pandas as pd
import joblib

# Load model and preprocessor
model = joblib.load("models/churn_random_forest.pkl")
preprocessor = joblib.load("models/churn_preprocessor.pkl")

# Get transformed feature names
feature_names = preprocessor.get_feature_names_out()

# Get importance
importance = model.feature_importances_

# Create dataframe
feature_importance = pd.DataFrame({
    "feature": feature_names,
    "importance": importance
})

# Sort
feature_importance = feature_importance.sort_values(
    by="importance",
    ascending=False
)

print("\n========================================")
print("TOP 20 CHURN FEATURES")
print("========================================")

print(
    feature_importance.head(20).to_string(index=False)
)

# Save results
feature_importance.to_csv(
    "data/feature_importance.csv",
    index=False
)

print("\nFeature importance saved to:")
print("data/feature_importance.csv")