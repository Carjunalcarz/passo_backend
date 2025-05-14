"""Module containing Pydantic schemas for approval sections in the Real Property Tax Assessment System."""
from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class ApprovalSection(BaseModel):
    """Schema for approval section data validation and serialization.
    
    This schema defines the structure for approval section data,
    including all necessary dates and approver information.
    """

    owner_id: Optional[int] = None
    tdn: Optional[str] = None
    appraised_by: Optional[str] = Field(None, alias="appraisedBy")
    appraised_date: Optional[date] = Field(None, alias="appraisedDate")
    recommending_approval: Optional[str] = Field(None, alias="recommendingApproval")
    municipality_assessor_date: Optional[date] = Field(
        None, alias="municipalityAssessorDate"
    )
    approved_by_province: Optional[str] = Field(None, alias="approvedByProvince")
    provincial_assessor_date: Optional[date] = Field(
        None, alias="provincialAssessorDate"
    )

    class Config:
        """Pydantic model configuration."""

        orm_mode = True
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "owner_id": 1,
                "tdn": "TDN123",
                "appraisedBy": "John Smith",
                "appraisedDate": "2024-03-20",
                "recommendingApproval": "Jane Doe",
                "municipalityAssessorDate": "2024-03-21",
                "approvedByProvince": "Bob Wilson",
                "provincialAssessorDate": "2024-03-22",
            }
        }
