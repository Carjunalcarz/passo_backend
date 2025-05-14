# schemas/ownerDetails_schema.py
from typing import Optional

from pydantic import BaseModel, Field


class OwnerDetails(BaseModel):
    id: Optional[int] = Field(
        default=None, description="Unique identifier for the owner"
    )
    owner: str = Field(
        # ...,
        description="Name of the owner",
        min_length=1,
    )
    ownerAddress: str = Field(
        # ...,
        description="Address of the owner",
        min_length=1,
    )
    admin_ben_user: str = Field(
        # ...,
        description="Administrative/Beneficial user",
        min_length=1,
    )
    transactionCode: str = Field(
        # ...,
        description="Transaction code for the record",
        min_length=1,
    )
    pin: str = Field(
        # ...,
        description="Personal Identification Number",
        min_length=1,
        unique=True,  # Making PIN unique as it's typically unique per person
    )
    tin: str = Field(
        # ...,
        description="Tax Identification Number",
        min_length=1,
        unique=True,  # Making TIN unique as it's typically unique per person
    )
    telNo: str = Field(
        # ...,
        description="Telephone Number",
        min_length=1,
    )
    td: str = Field(
        # ...,
        description="Tax Declaration Number",
        min_length=1,
    )

    class Config:
        schema_extra = {
            "example": {
                "owner": "John Doe",
                "ownerAddress": "123 Main St, City",
                "admin_ben_user": "Admin User",
                "transactionCode": "TRANS001",
                "pin": "1234567890",
                "tin": "123-456-789",
                "telNo": "+1234567890",
                "td": "TD2024-001",
            }
        }
        from_attributes = True
