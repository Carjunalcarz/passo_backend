"""Module containing the ApprovalSection model definition for the Real Property Tax Assessment System."""
from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database.database import Base


class ApprovalSectionModel(Base):
    """Model representing approval sections in the database.
    
    This model stores the approval workflow information for property assessments,
    including dates, approvers, and references to owner details.
    """

    __tablename__ = "approval_sections"
    __table_args__ = {"schema": "Assessor2025"}

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("Assessor2025.owner_details.id"))
    tdn = Column(String, unique=True)
    appraised_by = Column(String)
    appraised_date = Column(Date)
    recommending_approval = Column(String)
    municipality_assessor_date = Column(Date)
    approved_by_province = Column(String)
    provincial_assessor_date = Column(Date)

    # Relationship with owner
    owner_details = relationship("OwnerDetailsModel", back_populates="approval_sections")
