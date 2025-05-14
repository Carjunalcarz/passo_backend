from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from database.database import Base


class OwnerDetailsModel(Base):
    __tablename__ = "owner_details"
    __table_args__ = {"schema": "Assessor2025"}
    # Simple auto-incrementing ID
    id = Column(Integer, primary_key=True, autoincrement=True)

    owner = Column(String)
    ownerAddress = Column(String)
    admin_ben_user = Column(String)
    transactionCode = Column(String)
    pin = Column(String, unique=True)
    tin = Column(String, unique=True)
    telNo = Column(String)
    td = Column(String)

    # Relationship with approval sections
    approval_sections = relationship(
        "ApprovalSectionModel", back_populates="owner_details"
    )
