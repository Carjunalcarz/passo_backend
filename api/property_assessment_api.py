from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from database.database import get_db
from models import property_assessment_model as models
from schemas import property_assessment_schema as schemas
from authentication.user_auth import verify_token
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    username = verify_token(token)
    if username is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return username

@router.get("/assessments", response_model=schemas.PaginatedAssessmentResponse)
def get_assessments(
    skip: int = Query(0, ge=0),
    limit: int = Query(0, le=300000),
    municipality: str | None = Query(None),
    barangay: str | None = Query(None),
    classification: str | None = Query(None),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(models.PropertyAssessmentClean)

    filters = []
    if municipality:
        filters.append(models.PropertyAssessmentClean.municipality.ilike(f"%{municipality}%"))
    if barangay:
        filters.append(models.PropertyAssessmentClean.barangay.ilike(f"%{barangay}%"))
    if classification:
        filters.append(models.PropertyAssessmentClean.classification.ilike(f"%{classification}%"))

    if filters:
        query = query.filter(and_(*filters))

    total = query.count()
    assessments = query.offset(skip).limit(limit).all()

    return {
        "data": assessments,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.post("/assessments", response_model=schemas.PropertyAssessment)
def create_assessment(
    assessment: schemas.PropertyAssessment,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if assessment with the same TDN already exists
    existing_assessment = db.query(models.PropertyAssessmentClean).filter(
        models.PropertyAssessmentClean.tdn == assessment.tdn
    ).first()
    
    if existing_assessment:
        raise HTTPException(
            status_code=400,
            detail="Assessment with this TDN already exists"
        )
    
    # Create new assessment
    db_assessment = models.PropertyAssessmentClean(**assessment.dict())
    db.add(db_assessment)
    db.commit()
    db.refresh(db_assessment)
    return db_assessment

@router.put("/assessments/{tdn}", response_model=schemas.PropertyAssessment)
def update_assessment(
    tdn: str,
    assessment: schemas.PropertyAssessment,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_assessment = db.query(models.PropertyAssessmentClean).filter(models.PropertyAssessmentClean.tdn == tdn).first()
    if not db_assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    # Update all fields from the request
    for field, value in assessment.dict(exclude_unset=True).items():
        setattr(db_assessment, field, value)
    
    db.commit()
    db.refresh(db_assessment)
    return db_assessment

@router.delete("/assessments/{tdn}")
def delete_assessment(
    tdn: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_assessment = db.query(models.PropertyAssessmentClean).filter(models.PropertyAssessmentClean.tdn == tdn).first()
    if not db_assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    db.delete(db_assessment)
    db.commit()
    return {"message": "Assessment deleted successfully"}
