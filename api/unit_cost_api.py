from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from schemas.unit_cost_schema import (
    UnitCostCreate, 
    UnitCostUpdate, 
    UnitCostResponse, 
    UnitCostListResponse,
    UnitCostPaginatedResponse
)
from models.unit_cost_model import UnitCostModel
from database.database import get_db
from fastapi.security import OAuth2PasswordBearer
from api.add_assessment_api import verify_token
from datetime import datetime
from typing import Optional

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> str:
    username = verify_token(token)
    if username is None:
        raise HTTPException(status_code=401, detail='Invalid token')
    return username

@router.post("/unit-cost", response_model=dict)
async def create_unit_cost(
    unit_cost_data: UnitCostCreate, 
    db: Session = Depends(get_db), 
    current_user: str = Depends(get_current_user)
):
    try:
        unit_cost = UnitCostModel(
            struct_class_type=unit_cost_data.struct_class_type,
            category=unit_cost_data.category,
            smv_year=unit_cost_data.smv_year,
            smv_code=unit_cost_data.smv_code,
            smv_name=unit_cost_data.smv_name,
            unit_cost=unit_cost_data.unit_cost,
            remarks=unit_cost_data.remarks,
            date_input=datetime.now().strftime("%Y-%m-%d"),
            inputed_by=current_user,
            increase=unit_cost_data.increase,
        )

        db.add(unit_cost)
        db.commit()
        db.refresh(unit_cost)
        return {"message": "Unit cost created successfully", "unit_cost_id": unit_cost.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/unit-costs", response_model=UnitCostPaginatedResponse)
async def get_unit_cost(
    skip: int = Query(0, ge=0),
    limit: int = Query(0, le=300000),
    db: Session = Depends(get_db), 
    current_user: str = Depends(get_current_user)
):
    try:
        # Get total count
        total = db.query(UnitCostModel).count()
        
        # Get paginated results
        unit_costs = db.query(UnitCostModel).offset(skip).limit(limit).all()
        
        # Convert SQLAlchemy objects to Pydantic models
        unit_cost_responses = [UnitCostResponse.from_orm(unit_cost) for unit_cost in unit_costs]
        
        return UnitCostPaginatedResponse(
            data=unit_cost_responses,
            total=total,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Keep the original endpoint for backward compatibility
@router.get("/unit-cost/all", response_model=UnitCostListResponse)
async def get_all_unit_costs(db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    try:
        unit_costs = db.query(UnitCostModel).all()
        # Convert SQLAlchemy objects to Pydantic models
        unit_cost_responses = [UnitCostResponse.from_orm(unit_cost) for unit_cost in unit_costs]
        return UnitCostListResponse(
            message="Unit costs retrieved successfully",
            unit_costs=unit_cost_responses
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/unit-cost/{unit_cost_id}", response_model=dict)
async def get_unit_cost_by_id(
    unit_cost_id: int, 
    db: Session = Depends(get_db), 
    current_user: str = Depends(get_current_user)
):
    try:
        unit_cost = db.query(UnitCostModel).filter(UnitCostModel.id == unit_cost_id).first()
        if not unit_cost:
            raise HTTPException(status_code=404, detail="Unit cost not found")
        
        # Convert to Pydantic model for proper serialization
        unit_cost_response = UnitCostResponse.from_orm(unit_cost)
        return {"message": "Unit cost retrieved successfully", "unit_cost": unit_cost_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/unit-cost/{unit_cost_id}", response_model=dict)
async def update_unit_cost(
    unit_cost_id: int, 
    unit_cost_data: UnitCostUpdate, 
    db: Session = Depends(get_db), 
    current_user: str = Depends(get_current_user)
):
    try:
        unit_cost = db.query(UnitCostModel).filter(UnitCostModel.id == unit_cost_id).first()
        if not unit_cost:
            raise HTTPException(status_code=404, detail="Unit cost not found")
        
        # Update only provided fields
        update_data = unit_cost_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(unit_cost, field, value)
        
        db.commit()
        db.refresh(unit_cost)
        return {"message": "Unit cost updated successfully", "unit_cost_id": unit_cost.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/unit-cost/{unit_cost_id}", response_model=dict)
async def delete_unit_cost(
    unit_cost_id: int, 
    db: Session = Depends(get_db), 
    current_user: str = Depends(get_current_user)
):
    try:
        unit_cost = db.query(UnitCostModel).filter(UnitCostModel.id == unit_cost_id).first()
        if not unit_cost:           
            raise HTTPException(status_code=404, detail="Unit cost not found")
        db.delete(unit_cost)
        db.commit()
        return {"message": "Unit cost deleted successfully", "unit_cost_id": unit_cost_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




