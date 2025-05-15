from pydantic import BaseModel
from typing import List, Optional

class AdditionalItemValue(BaseModel):
    label: str
    ratePerSqM: Optional[float] = None
    percentage: Optional[float] = None

class AdditionalItemEntry(BaseModel):
    id: int
    label: str
    value: AdditionalItemValue
    quantity: float
    amount: float
    description: Optional[str] = None

class AdditionalItems(BaseModel):
    items: List[AdditionalItemEntry]
    total: float
    subTotal: float

    class Config:
        from_attributes = True