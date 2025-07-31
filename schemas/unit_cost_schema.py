from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal

# For creating new unit costs
class UnitCostCreate(BaseModel):
    struct_class_type: Optional[str] = None
    category: Optional[str] = None
    smv_year: Optional[str] = None
    smv_code: Optional[str] = None
    smv_name: Optional[str] = None
    unit_cost: Optional[float] = None
    remarks: Optional[str] = None
    date_input: Optional[str] = None
    inputed_by: Optional[str] = None
    increase: Optional[float] = None

# For updating unit costs
class UnitCostUpdate(BaseModel):
    struct_class_type: Optional[str] = None
    category: Optional[str] = None
    smv_year: Optional[str] = None
    smv_code: Optional[str] = None
    smv_name: Optional[str] = None
    unit_cost: Optional[float] = None
    remarks: Optional[str] = None
    date_input: Optional[str] = None
    inputed_by: Optional[str] = None
    increase: Optional[float] = None

# For returning a single unit cost
class UnitCostResponse(BaseModel):
    id: int
    struct_class_type: Optional[str] = None
    category: Optional[str] = None
    smv_year: Optional[str] = None
    smv_code: Optional[str] = None
    smv_name: Optional[str] = None
    unit_cost: Optional[float] = None
    remarks: Optional[str] = None
    date_input: Optional[str] = None
    inputed_by: Optional[str] = None
    increase: Optional[float] = None

    class Config:
        from_attributes = True

# For returning a list of unit costs
class UnitCostListResponse(BaseModel):
    message: str
    unit_costs: List[UnitCostResponse]

# For paginated responses
class UnitCostPaginatedResponse(BaseModel):
    data: List[UnitCostResponse]
    total: int
    skip: int
    limit: int
