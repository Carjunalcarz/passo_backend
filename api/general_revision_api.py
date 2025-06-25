from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from authentication.user_auth import verify_token
from database.database import get_db
from models import general_revision_model
from schemas import general_revision_schema

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> str:
    username = verify_token(token)
    if username is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return username


@router.get(
    "/get-general-revision",
    response_model=general_revision_schema.PaginatedAssessmentResponse,
)
def get_assessments(
    skip: int = Query(0, ge=0),
    limit: int = Query(0, le=300000),
    municipality: str | None = Query(None),
    barangay: str | None = Query(None),
    classification: str | None = Query(None),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(general_revision_model.GeneralRevisionModel)

    filters = []
    if municipality:
        filters.append(
            general_revision_model.GeneralRevisionModel.municipality.ilike(
                f"%{municipality}%"
            )
        )
    if barangay:
        filters.append(
            general_revision_model.GeneralRevisionModel.barangay.ilike(f"%{barangay}%")
        )
    if classification:
        filters.append(
            general_revision_model.GeneralRevisionModel.classification.ilike(
                f"%{classification}%"
            )
        )

    if filters:
        query = query.filter(and_(*filters))

    total = query.count()
    sum_market_val = query.with_entities(
        func.sum(general_revision_model.GeneralRevisionModel.market_val)
    ).scalar()
    sum_ass_value = query.with_entities(
        func.sum(general_revision_model.GeneralRevisionModel.ass_value)
    ).scalar()
    sum_area = query.with_entities(
        func.sum(general_revision_model.GeneralRevisionModel.area)
    ).scalar()
    assessments = query.offset(skip).limit(limit).all()

    return {
        "data": assessments,
        "total": total,
        "skip": skip,
        "limit": limit,
        "sum_market_val": sum_market_val,
        "sum_ass_value": sum_ass_value,
        "sum_area": sum_area,
    }


@router.post("/create-general-revision")
async def create_general_revision(
    payload: general_revision_schema.PropertyAssessmentCreate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    new_property = general_revision_model.GeneralRevisionModel(**payload.dict())
    db.add(new_property)
    db.commit()
    db.refresh(new_property)
    return new_property


@router.put("/update-general-revision")
async def update_general_revision(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    pass
