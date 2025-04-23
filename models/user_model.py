from sqlalchemy import Column, Integer, String
from database.database import Base
class User(Base):
    __tablename__ = "users"
    __table_args__ = {'schema': 'Assessor2025'}
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

