from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, validator


class ApprovalSection(BaseModel):
    id: Optional[int] = Field(
        default=None, description="Unique identifier for the assessment"
    )
    owner_id: Optional[int] = Field(
        default=None, description="Foreign key reference to the owner"
    )
    tdn: str = Field(
        # ...,  # ... means the field is required
        description="Tax Declaration Number - Primary Identifier",
        min_length=1,
        unique=True,  # indicates this field should be unique
    )
    # appraisedBy
    appraisedBy: str = Field(
        # ...,  # ... means the field is required
        description="Name of the person who appraised",
        min_length=1,
    )

    appraisedDate: str = Field(
        # ...,
        description="Date when the appraisal was done"
    )

    recommendingApproval: str = Field(
        # ...,
        description="Name of person recommending the approval",
        min_length=1,
    )

    municipalityAssessorDate: str = Field(
        # ...,
        description="Date of municipality assessor review"
    )

    approvedByProvince: str = Field(
        # ...,
        description="Name of provincial authority who approved",
        min_length=1,
    )

    provincialAssessorDate: str = Field(
        # ...,
        description="Date of provincial assessor review"
    )

    @validator("appraisedDate", "municipalityAssessorDate", "provincialAssessorDate")
    def validate_dates(cls, v):
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("Date must be in format YYYY-MM-DD")

    class Config:
        schema_extra = {
            "example": {
                "appraisedBy": "John Doe",
                "appraisedDate": "2024-03-20",
                "recommendingApproval": "Jane Smith",
                "municipalityAssessorDate": "2024-03-21",
                "approvedByProvince": "Robert Johnson",
                "provincialAssessorDate": "2024-03-22",
            }
        }
