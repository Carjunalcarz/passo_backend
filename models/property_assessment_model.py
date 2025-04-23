from sqlalchemy import Column, String, Numeric, Date
from database.database import Base

class PropertyAssessmentClean(Base):
    __tablename__ = "property_assessment_clean"
    __table_args__ = {"schema": "Assessor2025"}

    tdn = Column(String(50), primary_key=True)
    market_val = Column(Numeric(15, 2))
    ass_value = Column(Numeric(15, 2))
    sub_class = Column(String(50))
    eff_date = Column(Date)
    classification = Column(String(50))
    ass_level = Column(Numeric(5, 2))
    area = Column(Numeric(15, 2))
    taxability = Column(String(20))
    gr_code = Column(String(20))
    gr = Column(String(100))
    mun_code = Column(String(20))
    municipality = Column(String(100))
    barangay_code = Column(String(20))
    barangay = Column(String(100))
