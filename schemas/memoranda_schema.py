from pydantic import BaseModel
from datetime import date

class Memorandum(BaseModel):
    date: date
    details: str

    class Config:
        from_attributes = True