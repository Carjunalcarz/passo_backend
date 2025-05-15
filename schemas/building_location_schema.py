from typing import Optional
from pydantic import BaseModel, Field

class BuildingLocation(BaseModel):
    address_municipality: Optional[str] = Field(None)
    address_barangay: Optional[str] = Field(None)
    street: Optional[str] = Field(None)
    address_province: Optional[str] = Field(None)

    class Config:
        from_attributes = True