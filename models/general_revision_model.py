from sqlalchemy import Column, DateTime, Integer, Numeric, String, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

from database.database import engine

Base = declarative_base()


class GeneralRevisionModel(Base):
    __tablename__ = "general_revision"
    __table_args__ = {"schema": "Assessor2025"}

    id = Column(Integer, primary_key=True, index=True)
    pin = Column(
        String(50), nullable=False, index=True, comment="Property Identification Number"
    )
    name = Column(String(255), nullable=True, comment="Property Owner Name")
    tdn = Column(
        String(50), nullable=True, index=True, comment="Tax Declaration Number"
    )
    market_val = Column(Numeric(15, 2), nullable=True, comment="Market Value")
    ass_value = Column(Numeric(15, 2), nullable=True, comment="Assessed Value")
    area = Column(Numeric(10, 2), nullable=True, comment="Property Area")
    taxability = Column(String(50), nullable=True, comment="Taxability Status")
    sub_class = Column(
        String(100), nullable=True, comment="Property Sub Classification"
    )
    classification = Column(
        String(100), nullable=True, comment="Property Classification"
    )
    trans_cd = Column(String(20), nullable=True, comment="Transaction Code")
    gr = Column(String(100), nullable=True, comment="Geographical Region")
    gr_code = Column(String(20), nullable=True, comment="Geographical Region Code")
    mun_code = Column(String(20), nullable=True, comment="Municipality Code")
    municipality = Column(String(100), nullable=True, comment="Municipality Name")
    b_code = Column(String(20), nullable=True, comment="Barangay Code")
    barangay = Column(String(100), nullable=True, comment="Barangay Name")
    date_input = Column(DateTime, default=func.now(), comment="Date of Input")
    inputed_by = Column(String(100), nullable=True, comment="Input By User")


# Create schema if it doesn't exist, then create all tables
try:

    Base.metadata.create_all(bind=engine)
    print("General Revision table created successfully")
except Exception as e:
    print(f"Error creating table: {e}")
    print("Please ensure your database is running and accessible")
