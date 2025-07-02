from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel


class PropertyAssessmentCreate(BaseModel):
    id: int
    tdn: Optional[str]
    pin: str
    name: Optional[str]
    market_val: Optional[float]
    ass_value: Optional[float]
    area: Optional[float]
    unit_value: Optional[float]
    kind: Optional[str]
    ass_level: Optional[str]
    classification: Optional[str]
    sub_class: Optional[str]
    taxability: Optional[str]
    trans_cd: Optional[str]
    tax_beg_yr: Optional[str]
    eff_date: Optional[str]
    owner_no: Optional[str]
    mun_code: Optional[str]
    municipality: Optional[str]
    bcode: Optional[str]
    barangay: Optional[str]
    gr_code: Optional[str]
    gr: Optional[str]
    date_input: Optional[Union[str, datetime]]
    inputed_by: Optional[str]


    class Config:
        from_attributes = True


class PaginatedAssessmentResponse(BaseModel):
    data: List[PropertyAssessmentCreate]
    total: int
    skip: int
    limit: int


 
