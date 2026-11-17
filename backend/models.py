from sqlalchemy import Column, Integer, String
from backend.database import Base


class RareDisease(Base):
    __tablename__ = "rare_diseases"

    id = Column(Integer, primary_key=True, autoincrement=True)
    orpha_code = Column(String)
    name = Column(String)
    disorder_type = Column(String)
    disorder_group = Column(String)
    icd_11 = Column(String)
    mondo = Column(String)
    icd_10 = Column(String)
    omim = Column(String)
    umls = Column(String)
    mesh = Column(String)
    meddra = Column(String)
    gard = Column(String)
    disease_name = Column(String)
    age_of_onset = Column(String)
    type_of_inheritance = Column(String)