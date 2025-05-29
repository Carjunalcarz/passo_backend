from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class PropertyAssessmentCreate(BaseModel):
    pin: str
    name: str
    tdn: str
    market_val: Optional[float] = 0.0
    ass_value: Optional[float] = 0.0
    area: Optional[float] = 0.0
    taxability: str
    sub_class: str
    classification: str
    trans_cd: str
    gr: Optional[str] = None
    gr_code: str
    mun_code: str
    municipality: str
    b_code: str
    barangay: str
    date_input: datetime
    inputed_by: str

    class Config:
        from_attributes = True


class PaginatedAssessmentResponse(BaseModel):
    data: List[PropertyAssessmentCreate]
    total: int
    skip: int
    limit: int
