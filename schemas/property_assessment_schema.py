from pydantic import BaseModel
from datetime import date
from typing import Optional
from typing import List

class EffectivityOfAssessment(BaseModel):
    quarter: Optional[str] = None

class AssessmentItem(BaseModel):
    id: str
    area: float
    unitValue: float
    smv: float
    baseMarketValue: float
    depreciationPercentage: float
    depreciatorCost: float
    marketValue: float
    buildingCategory: str

class PropertyAssessment(BaseModel):
    tdn: str
    market_val: Optional[float]
    ass_value: Optional[float]
    sub_class: Optional[str]
    eff_date: Optional[date]
    classification: Optional[str]
    ass_level: Optional[float]
    area: Optional[float]
    taxability: Optional[str]
    gr_code: Optional[str]
    gr: Optional[str]
    mun_code: Optional[str]
    municipality: Optional[str]
    barangay_code: Optional[str]
    barangay: Optional[str]
    assessmentLevel: float
    assessmentValue: float
    totalArea: float
    marketValue: float
    buildingCategory: str
    effectivityOfAssessment: EffectivityOfAssessment
    items: List[AssessmentItem]

    class Config:
        from_attributes = True

class PaginatedAssessmentResponse(BaseModel):
    data: List[PropertyAssessment]
    total: int
    skip: int
    limit: int