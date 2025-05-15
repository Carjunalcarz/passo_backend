from typing import Optional
from pydantic import BaseModel, Field

class LandReference(BaseModel):
    land_owner: Optional[str] = Field(None)
    block_no: Optional[str] = Field(None)
    tdn_no: Optional[str] = Field(None)
    pin: Optional[str] = Field(None)
    lot_no: Optional[str] = Field(None)
    survey_no: Optional[str] = Field(None)
    area: Optional[str] = Field(None)

    class Config:
        from_attributes = True