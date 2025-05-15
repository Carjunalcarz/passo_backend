from pydantic import BaseModel
from typing import Optional

class PropertyAppraisal(BaseModel):
    buildingType: Optional[str] = None
    buildingStructure: Optional[str] = None
    totalArea: Optional[float] = None
    unitValue: Optional[float] = None
    smv: Optional[float] = None
    baseMarketValue: Optional[float] = None
    depreciation: Optional[float] = None
    marketValue: Optional[float] = None

    class Config:
        from_attributes = True