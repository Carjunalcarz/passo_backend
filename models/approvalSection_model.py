from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database.database import Base


class ApprovalSectionModel(Base):
    __tablename__ = "approval_sections"
    __table_args__ = {"schema": "Assessor2025"}

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("Assessor2025.owner_details.id"))
    tdn = Column(String, unique=True)
    appraisedBy = Column(String)
    appraisedDate = Column(Date)
    recommendingApproval = Column(String)
    municipalityAssessorDate = Column(Date)
    approvedByProvince = Column(String)
    provincialAssessorDate = Column(Date)

    # Relationship with owner
    owner_details = relationship(
        "OwnerDetailsModel", back_populates="approval_sections"
    )
