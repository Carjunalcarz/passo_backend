from pydantic import BaseModel
from typing import List
from datetime import date

class SupersededRecord(BaseModel):
    pin: str
    tdArpNo: str
    totalAssessedValue: str
    previousOwner: str
    dateOfEffectivity: date
    date: date
    assessment: str
    taxMapping: str
    records: str

class RecordOfSupersededAssessment(BaseModel):
    records: List[SupersededRecord]

    class Config:
        from_attributes = True