from sqlalchemy import Column, DateTime, Integer, Numeric, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

from database.database import engine

Base = declarative_base()


class GeneralRevisionModel(Base):
    __tablename__ = "sta_july_general_revision"
    __table_args__ = {"schema": "Assessor2025"}

    id = Column(Integer, primary_key=True, index=True)
    tdn = Column(String(50), nullable=True)
    pin = Column(String(50), nullable=False, index=True)
    name = Column(String(1000), nullable=True)
    market_val = Column(Numeric(15, 2), nullable=True)
    ass_value = Column(Numeric(15, 2), nullable=True)
    area = Column(Numeric(10, 2), nullable=True)
    unit_value = Column(Numeric(15, 2), nullable=True)
    kind = Column(String(100), nullable=True)
    ass_level = Column(String(50), nullable=True)
    classification = Column(String(100), nullable=True)
    sub_class = Column(String(100), nullable=True)
    taxability = Column(String(50), nullable=True)
    trans_cd = Column(String(20), nullable=True)
    tax_beg_yr = Column(String(20), nullable=True)
    eff_date = Column(String(20), nullable=True)
    owner_no = Column(String(100), nullable=True)
    mun_code = Column(String(20), nullable=True)
    municipality = Column(String(100), nullable=True)
    bcode = Column(String(20), nullable=True)
    barangay = Column(String(100), nullable=True)
    gr_code = Column(String(20), nullable=True)
    gr = Column(String(100), nullable=True)
    date_input = Column(String(20), default=func.now())
    inputed_by = Column(String(100), nullable=True)


# Create schema if it doesn't exist, then create all tables
try:
    Base.metadata.create_all(bind=engine)
    print("General Revision table created successfully")
except Exception as e:
    print(f"Error creating table: {e}")
    print("Please ensure your database is running and accessible")
