import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

df = pd.read_csv("data/rare_diseases_complete.csv")

df.columns = [
    "orpha_code",
    "name",
    "disorder_type",
    "disorder_group",
    "icd_11",
    "mondo",
    "icd_10",
    "omim",
    "umls",
    "mesh",
    "meddra",
    "gard",
    "disease_name",
    "age_of_onset",
    "type_of_inheritance"
]

df.to_sql(
    "rare_diseases",
    engine,
    if_exists="replace",
    index=False
)

print(f"Successfully imported {len(df)} records.")