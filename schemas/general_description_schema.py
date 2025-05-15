from typing import Optional
from pydantic import BaseModel, Field
from datetime import date

class GeneralDescription(BaseModel):
    building_permit_no: Optional[str] = Field(None)
    certificate_of_completion_issued_on: Optional[date] = Field(None)
    certificate_of_occupancy_issued_on: Optional[date] = Field(None)
    date_of_occupied: Optional[date] = Field(None)
    bldg_age: Optional[str] = Field(None)
    no_of_storeys: Optional[str] = Field(None)
    area_of_1st_floor: Optional[str] = Field(None)
    area_of_2nd_floor: Optional[str] = Field(None)
    area_of_3rd_floor: Optional[str] = Field(None)
    area_of_4th_floor: Optional[str] = Field(None)
    total_floor_area: Optional[float] = Field(None)
    kind_of_bldg: Optional[str] = Field(None)
    structural_type: Optional[str] = Field(None)
    unitValue: Optional[float] = Field(None)

    class Config:
        from_attributes = True