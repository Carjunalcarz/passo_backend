"""Module containing the OwnerDetails model definition for the Real Property Tax Assessment System."""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from database.database import Base


class OwnerDetailsModel(Base):
    """Model representing property owner details in the database.
    
    This model stores essential information about property owners,
    including personal identification and contact details.
    """

    __tablename__ = 'owner_details'
    __table_args__ = {'schema': 'Assessor2025'}
    
    # Simple auto-incrementing ID
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    owner = Column(String)
    owner_address = Column(String)
    admin_ben_user = Column(String)
    transaction_code = Column(String)
    pin = Column(String, unique=True)
    tin = Column(String, unique=True)
    tel_no = Column(String)
    td = Column(String)

    # Relationship with approval sections
    approval_sections = relationship('ApprovalSectionModel', back_populates='owner_details')
