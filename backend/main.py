import joblib
import os
import pandas as pd
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from backend.database import get_db


app = FastAPI(
    title="Rare Disease Healthcare Intelligence API",
    description="Backend API for rare disease analytics",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "message": "Rare Disease Healthcare Intelligence API is running"
    }


@app.get("/diseases/count")
def disease_count(db: Session = Depends(get_db)):
    result = db.execute(
        text("SELECT COUNT(*) FROM rare_diseases")
    )

    return {
        "total_diseases": result.scalar()
    }
from fastapi import Query


@app.get("/diseases/search")
def search_diseases(
    q: str = "",
    disorder_type: str = "",
    disorder_group: str = "",
    db: Session = Depends(get_db)
):
    query = """
        SELECT *
        FROM rare_diseases
        WHERE
            (
                LOWER(name::text) LIKE LOWER(:search)
                OR LOWER(disease_name::text) LIKE LOWER(:search)
                OR LOWER(orpha_code::text) LIKE LOWER(:search)
                OR LOWER(gard::text) LIKE LOWER(:search)
            )
    """

    params = {
        "search": f"%{q}%"
    }

    if disorder_type and disorder_type != "All":
        query += """
            AND disorder_type::text = :disorder_type
        """
        params["disorder_type"] = disorder_type

    if disorder_group and disorder_group != "All":
        query += """
            AND disorder_group::text = :disorder_group
        """
        params["disorder_group"] = disorder_group

    query += " LIMIT 50"

    result = db.execute(
        text(query),
        params
    ).mappings().all()

    return [dict(row) for row in result]
@app.get("/analytics")
def analytics(db: Session = Depends(get_db)):

    total = db.execute(
        text("SELECT COUNT(*) FROM rare_diseases")
    ).scalar()

    disorder_types = db.execute(
        text("""
            SELECT disorder_type, COUNT(*) AS count
            FROM rare_diseases
            GROUP BY disorder_type
            ORDER BY count DESC
        """)
    ).fetchall()

    disorder_groups = db.execute(
        text("""
            SELECT disorder_group, COUNT(*) AS count
            FROM rare_diseases
            GROUP BY disorder_group
            ORDER BY count DESC
            LIMIT 10
        """)
    ).fetchall()

    return {
        "total_diseases": total,
        "disorder_types": [
            {
                "type": row.disorder_type,
                "count": row.count
            }
            for row in disorder_types
        ],
        "disorder_groups": [
            {
                "group": row.disorder_group,
                "count": row.count
            }
            for row in disorder_groups
        ]
    }
@app.get("/diseases/{orpha_code}")
def disease_details(
    orpha_code: str,
    db: Session = Depends(get_db)
):
    result = db.execute(
        text("""
            SELECT *
            FROM rare_diseases
            WHERE orpha_code::text = :orpha_code
            LIMIT 1
        """),
        {"orpha_code": orpha_code}
    ).mappings().first()

    if not result:
        return {
            "message": "Disease not found"
        }

    return dict(result)
@app.get("/analytics/age-onset")
def age_onset_analytics(db: Session = Depends(get_db)):

    result = db.execute(
        text("""
            SELECT age_of_onset, COUNT(*) AS count
            FROM rare_diseases
            WHERE age_of_onset IS NOT NULL
              AND age_of_onset != ''
            GROUP BY age_of_onset
            ORDER BY count DESC
        """)
    ).fetchall()

    return [
        {
            "age_of_onset": row.age_of_onset,
            "count": row.count
        }
        for row in result
    ]
@app.get("/ml/clusters")
def get_ml_clusters():
    model_path = "ml/disease_cluster_model.pkl"

    if not os.path.exists(model_path):
        return {"error": "ML model not found"}

    model = joblib.load(model_path)

    df = pd.read_csv("data/rare_diseases_complete.csv")

    features = [
        "DisorderType",
        "DisorderGroup",
        "AgeOfOnset",
        "TypeOfInheritance"
    ]

    data = df[features].fillna("Unknown")

    df["Cluster"] = model.predict(data)

    distribution = df["Cluster"].value_counts().sort_index()

    return {
        "total_diseases": len(df),
        "clusters": [
            {
                "cluster": int(cluster),
                "count": int(count)
            }
            for cluster, count in distribution.items()
        ]
    }
@app.get("/ml/cluster-summary")
def cluster_summary():
    model_path = "ml/disease_cluster_model.pkl"

    if not os.path.exists(model_path):
        return {"error": "ML model not found"}

    model = joblib.load(model_path)

    df = pd.read_csv("data/rare_diseases_complete.csv")

    features = [
        "DisorderType",
        "DisorderGroup",
        "AgeOfOnset",
        "TypeOfInheritance"
    ]

    data = df[features].fillna("Unknown")

    df["Cluster"] = model.predict(data)

    summary = []

    for cluster in sorted(df["Cluster"].unique()):

        cluster_data = df[df["Cluster"] == cluster]

        summary.append({
            "cluster": int(cluster),
            "disease_count": int(len(cluster_data)),
            "common_disorder_type": str(
                cluster_data["DisorderType"]
                .value_counts()
                .idxmax()
            ),
            "common_disorder_group": str(
                cluster_data["DisorderGroup"]
                .value_counts()
                .idxmax()
            ),
            "common_age_of_onset": str(
                cluster_data["AgeOfOnset"]
                .value_counts()
                .idxmax()
            ),
            "common_inheritance": str(
                cluster_data["TypeOfInheritance"]
                .value_counts()
                .idxmax()
            )
        })

    return {
        "clusters": summary
    }
@app.get("/ml/similar-diseases")
def similar_diseases(
    orpha_code: str,
    db: Session = Depends(get_db)
):
    disease = db.execute(
        text("""
            SELECT *
            FROM rare_diseases
            WHERE orpha_code::text = :orpha_code
            LIMIT 1
        """),
        {"orpha_code": orpha_code}
    ).mappings().first()

    if not disease:
        return {
            "message": "Disease not found"
        }

    results = db.execute(
        text("""
            SELECT *
            FROM rare_diseases
            WHERE disorder_type::text = :disorder_type
              AND disorder_group::text = :disorder_group
              AND orpha_code::text != :orpha_code
            LIMIT 10
        """),
        {
            "disorder_type": str(disease["disorder_type"]),
            "disorder_group": str(disease["disorder_group"]),
            "orpha_code": str(orpha_code)
        }
    ).mappings().all()

    return {
        "reference_disease": disease["name"],
        "similar_diseases": [
            {
                "orpha_code": row["orpha_code"],
                "name": row["name"],
                "disorder_type": row["disorder_type"],
                "disorder_group": row["disorder_group"],
                "age_of_onset": row["age_of_onset"],
                "type_of_inheritance": row["type_of_inheritance"]
            }
            for row in results
        ]
    }