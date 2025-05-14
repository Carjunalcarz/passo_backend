# schemas/ownerDetails_schema.py
"""Module containing Pydantic schemas for owner details in the Real Property Tax Assessment System."""
from typing import Optional

from pydantic import BaseModel, Field


class OwnerDetails(BaseModel):
    """Schema for owner details data validation and serialization.
    
    This schema defines the structure for owner details data,
    including personal identification and contact information.
    """

    owner: Optional[str] = None
    owner_address: Optional[str] = Field(None, alias="ownerAddress")
    admin_ben_user: Optional[str] = None
    transaction_code: Optional[str] = Field(None, alias="transactionCode")
    pin: Optional[str] = None
    tin: Optional[str] = None
    tel_no: Optional[str] = Field(None, alias="telNo")
    td: Optional[str] = None

    class Config:
        """Pydantic model configuration."""

        orm_mode = True
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
