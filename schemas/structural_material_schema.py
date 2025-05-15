from pydantic import BaseModel
from typing import Optional

class StructuralMaterial(BaseModel):
    walls_reinforced_concrete: Optional[bool] = False
    walls_plain_concrete: Optional[bool] = False
    walls_chpb: Optional[bool] = False
    walls_gi: Optional[bool] = False
    walls_build_wall: Optional[bool] = False
    walls_sawali: Optional[bool] = False
    walls_bamboo: Optional[bool] = False
    walls_other_checked: Optional[bool] = False
    walls_other: Optional[str] = None
    foundation_reinforced_concrete: Optional[bool] = False
    foundation_plain_concrete: Optional[bool] = False
    foundation_other_checked: Optional[bool] = False
    foundation_other: Optional[str] = None
    # ... (all other structural material fields)
    walls_rc_1st: Optional[bool] = False
    walls_rc_2nd: Optional[bool] = False
    walls_rc_3rd: Optional[bool] = False
    walls_rc_4th: Optional[bool] = False
    walls_rc_5th: Optional[bool] = False
    # ... (remaining fields as per your structure)

    class Config:
        from_attributes = True