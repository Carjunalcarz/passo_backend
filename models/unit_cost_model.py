from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy.sql import func
from database.database import engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class UnitCostModel(Base):
    __tablename__ = "unit_cost"
    __table_args__ = {"schema": "Assessor2025"}

    id = Column(Integer, primary_key=True, index=True)
    struct_class_type = Column(String(100), nullable=True)
    category = Column(String(100), nullable=True)
    smv_year = Column(String(20), nullable=True)
    smv_code = Column(String(100), nullable=True)
    smv_name = Column(String(100), nullable=True)
    unit_cost = Column(Numeric(15, 2), nullable=True)
    remarks = Column(String(1000), nullable=True)
    date_input = Column(String(20), nullable=True)
    inputed_by = Column(String(100), nullable=True)
    increase = Column(Numeric(15, 2), nullable=True)



# Create all tables defined in your models
try:
    Base.metadata.create_all(bind=engine, checkfirst=True)
    print("Unit cost table created successfully")
except Exception as e:
    print(f"Error creating table: {e}")
    print("Please ensure your database is running and accessible")


