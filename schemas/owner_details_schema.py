# schemas/ownerDetails_schema.py
"""Module containing Pydantic schemas for owner details in the Real Property Tax Assessment System."""
from typing import Optional

from pydantic import BaseModel, Field


class OwnerDetails(BaseModel):
    """Schema for owner details data validation and serialization.
    
    This schema defines the structure for owner details data,
    including personal identification and contact information.
    """

    owner: Optional[str] = Field(None)
    ownerAddress: Optional[str] = Field(None)
    admin_ben_user: Optional[str] = Field(None)
    transactionCode: Optional[str] = Field(None)
    pin: Optional[str] = Field(None)
    tin: Optional[str] = Field(None)
    telNo: Optional[str] = Field(None)
    td: Optional[str] = Field(None)

    class Config:
        """Pydantic model configuration."""

        from_attributes = True
        allow_population_by_field_name = True
        schema_extra = {
            'example': {
                'owner': 'John Doe',
                'ownerAddress': '123 Main St',
                'admin_ben_user': 'admin1',
                'transactionCode': 'TC123',
                'pin': '1234567890',
                'tin': '987654321',
                'telNo': '555-1234',
                'td': 'TD001',
            }
        }
