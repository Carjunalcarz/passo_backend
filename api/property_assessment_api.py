from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from authentication.user_auth import verify_token
from database.database import get_db
from models import general_revision_model as models
from schemas import general_revision_schema as schemas

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    username = verify_token(token)
    if username is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return username


@router.get("/property-assessments", response_model=schemas.PaginatedAssessmentResponse)
def get_assessments(
    skip: int = Query(0, ge=0),
    limit: int = Query(0, le=300000),
    municipality: str | None = Query(None),
    barangay: str | None = Query(None),
    classification: str | None = Query(None),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(models.GeneralRevisionModel)

    filters = []
    if municipality:
        filters.append(
            models.GeneralRevisionModel.municipality.ilike(f"%{municipality}%")
        )
    if barangay:
        filters.append(models.GeneralRevisionModel.barangay.ilike(f"%{barangay}%"))
    if classification:
        filters.append(
            models.GeneralRevisionModel.classification.ilike(f"%{classification}%")
        )

    if filters:
        query = query.filter(and_(*filters))

    total = query.count()
    assessments = query.offset(skip).limit(limit).all()

    return {"data": assessments, "total": total, "skip": skip, "limit": limit}


@router.post("/property-assessments", response_model=schemas.PropertyAssessmentCreate)
def create_assessment(
    assessment: schemas.PropertyAssessmentCreate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Check if assessment with the same TDN already exists
    existing_assessment = (
        db.query(models.GeneralRevisionModel)
        .filter(models.GeneralRevisionModel.tdn == assessment.tdn)
        .first()
    )

    if existing_assessment:
        raise HTTPException(
            status_code=400, detail="Assessment with this TDN already exists"
        )

    # Create new assessment
    db_assessment = models.GeneralRevisionModel(**assessment.dict())
    db.add(db_assessment)
    db.commit()
    db.refresh(db_assessment)
    return db_assessment


@router.put(
    "/property-assessments/{tdn}", response_model=schemas.PropertyAssessmentCreate
)
def update_assessment(
    tdn: str,
    assessment: schemas.PropertyAssessmentCreate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_assessment = (
        db.query(models.GeneralRevisionModel)
        .filter(models.GeneralRevisionModel.tdn == tdn)
        .first()
    )
    if not db_assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    # Update all fields from the request
    for field, value in assessment.dict(exclude_unset=True).items():
        setattr(db_assessment, field, value)

    db.commit()
    db.refresh(db_assessment)
    return db_assessment


@router.delete("/property-assessments/{tdn}")
def delete_assessment(
    tdn: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_assessment = (
        db.query(models.GeneralRevisionModel)
        .filter(models.GeneralRevisionModel.tdn == tdn)
        .first()
    )
    if not db_assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    db.delete(db_assessment)
    db.commit()
    return {"message": "Assessment deleted successfully"}


@router.get("/property-assessments/count/taxable")
def count_taxable_assessments(
    municipality: str | None = Query(None),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(models.GeneralRevisionModel).filter(
        models.GeneralRevisionModel.taxability == "1"
    )

    if municipality:
        query = query.filter(
            models.GeneralRevisionModel.municipality.ilike(f"%{municipality}%")
        )

    count = query.count()
    print(f"Count of taxable assessments: {count}")
    return {"count": count}


@router.get("/property-assessments/count/exempt")
def count_exempt_assessments(
    municipality: str | None = Query(None),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(models.GeneralRevisionModel).filter(
        models.GeneralRevisionModel.taxability == "0"
    )

    if municipality:
        query = query.filter(
            models.GeneralRevisionModel.municipality.ilike(f"%{municipality}%")
        )

    count = query.count()
    return {"count": count}


@router.get("/property-assessments/market-value/taxable")
def get_taxable_market_value(
    municipality: str | None = Query(None),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(func.sum(models.GeneralRevisionModel.market_val)).filter(
        models.GeneralRevisionModel.taxability == "1"
    )

    if municipality:
        query = query.filter(
            models.GeneralRevisionModel.municipality.ilike(f"%{municipality}%")
        )

    taxable_market_value = query.scalar()
    return {"taxable_market_value": taxable_market_value or 0}


@router.get("/property-assessments/market-value/exempt")
def get_exempt_market_value(
    municipality: str | None = Query(None),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(func.sum(models.GeneralRevisionModel.market_val)).filter(
        models.GeneralRevisionModel.taxability == "0"
    )

    if municipality:
        query = query.filter(
            models.GeneralRevisionModel.municipality.ilike(f"%{municipality}%")
        )

    exempt_market_value = query.scalar()
    return {"exempt_market_value": exempt_market_value or 0}


@router.get("/property-assessments/assessment-value/taxable")
def get_taxable_assessment_value(
    municipality: str | None = Query(None),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(func.sum(models.GeneralRevisionModel.ass_value)).filter(
        models.GeneralRevisionModel.taxability == "1"
    )

    if municipality:
        query = query.filter(
            models.GeneralRevisionModel.municipality.ilike(f"%{municipality}%")
        )

    taxable_assessment_value = query.scalar()
    return {"taxable_assessment_value": taxable_assessment_value or 0}


@router.get("/property-assessments/assessment-value/exempt")
def get_exempt_assessment_value(
    municipality: str | None = Query(None),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(func.sum(models.GeneralRevisionModel.ass_value)).filter(
        models.GeneralRevisionModel.taxability == "0"
    )

    if municipality:
        query = query.filter(
            models.GeneralRevisionModel.municipality.ilike(f"%{municipality}%")
        )

    exempt_assessment_value = query.scalar()
    return {"exempt_assessment_value": exempt_assessment_value or 0}


@router.get("/property-assessments/area/taxable")
def get_taxable_area(
    municipality: str | None = Query(None),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(func.sum(models.GeneralRevisionModel.area)).filter(
        models.GeneralRevisionModel.taxability == "1"
    )

    if municipality:
        query = query.filter(
            models.GeneralRevisionModel.municipality.ilike(f"%{municipality}%")
        )

    taxable_area = query.scalar()
    return {"taxable_area": taxable_area or 0}


@router.get("/property-assessments/area/exempt")
def get_exempt_area(
    municipality: str | None = Query(None),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(func.sum(models.GeneralRevisionModel.area)).filter(
        models.GeneralRevisionModel.taxability == "0"
    )

    if municipality:
        query = query.filter(
            models.GeneralRevisionModel.municipality.ilike(f"%{municipality}%")
        )

    exempt_area = query.scalar()
    return {"exempt_area": exempt_area or 0}
