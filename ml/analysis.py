import joblib
import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

# Load dataset
df = pd.read_csv("data/rare_diseases_complete.csv")

# Features used for clustering
features = [
    "DisorderType",
    "DisorderGroup",
    "AgeOfOnset",
    "TypeOfInheritance"
]

data = df[features].fillna("Unknown")

# Preprocessing
preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            features
        )
    ]
)

# K-Means model
model = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("kmeans", KMeans(
            n_clusters=5,
            random_state=42,
            n_init=10
        ))
    ]
)

# Train model
model.fit(data)

# Assign clusters
df["Cluster"] = model.predict(data)
joblib.dump(model, "ml/disease_cluster_model.pkl")
print("Model saved successfully.")

print("Disease clustering completed.")
print("\nCluster Distribution:")
print(df["Cluster"].value_counts().sort_index())

print("\nSample Results:")
print(
    df[
        [
            "Name",
            "DisorderType",
            "DisorderGroup",
            "AgeOfOnset",
            "TypeOfInheritance",
            "Cluster"
        ]
    ].head(10)
)
joblib.dump(model, "ml/disease_cluster_model.pkl")
print("Model saved successfully.")