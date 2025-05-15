"""Module containing Pydantic schemas for approval sections in the Real Property Tax Assessment System."""
from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class ApprovalSection(BaseModel):
    """Schema for approval section data validation and serialization.
    
    This schema defines the structure for approval section data,
    including all necessary dates and approver information.
    """

    appraisedBy: Optional[str] = Field(None)
    appraisedDate: Optional[date] = Field(None)
    recommendingApproval: Optional[str] = Field(None)
    municipalityAssessorDate: Optional[date] = Field(None)
    approvedByProvince: Optional[str] = Field(None)
    provincialAssessorDate: Optional[date] = Field(None)

    class Config:
        """Pydantic model configuration."""

        from_attributes = True
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "appraisedBy": "John Smith",
                "appraisedDate": "2024-03-20",
                "recommendingApproval": "Jane Doe",
                "municipalityAssessorDate": "2024-03-21",
                "approvedByProvince": "Bob Wilson",
                "provincialAssessorDate": "2024-03-22",
            }
        }
