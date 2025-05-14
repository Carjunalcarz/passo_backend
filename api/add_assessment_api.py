from datetime import datetime
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from authentication.user_auth import verify_token
from database.database import get_db
from models import ApprovalSectionModel, OwnerDetailsModel
from schemas.approvalSection_schema import ApprovalSection
from schemas.ownerDetails_schema import OwnerDetails

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    username = verify_token(token)
    if username is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return username


@router.post("/add-assessments/", response_model=Dict)
async def create_property_assessment(
    approval_section: ApprovalSection,
    owner_details: OwnerDetails,
    db: Session = Depends(get_db),
):
    """
    Create a new property assessment with approval section and owner details
    """
    try:
        # First, create or get the owner
        owner = (
            db.query(OwnerDetailsModel)
            .filter(
                (OwnerDetailsModel.pin == owner_details.pin)
                | (OwnerDetailsModel.tin == owner_details.tin)
            )
            .first()
        )

        if not owner:
            # Create new owner if doesn't exist
            try:
                owner = OwnerDetailsModel(
                    owner=owner_details.owner,
                    ownerAddress=owner_details.ownerAddress,
                    admin_ben_user=owner_details.admin_ben_user,
                    transactionCode=owner_details.transactionCode,
                    pin=owner_details.pin,
                    tin=owner_details.tin,
                    telNo=owner_details.telNo,
                    td=owner_details.td,
                )
                db.add(owner)
                db.flush()  # This will generate the owner.id
            except Exception as owner_error:
                db.rollback()
                raise HTTPException(
                    status_code=400,
                    detail={
                        "message": "Failed to create owner details",
                        "error": str(owner_error),
                    },
                )

        # Create the assessment with owner reference
        try:
            assessment = ApprovalSectionModel(
                owner_id=owner.id,
                tdn=approval_section.tdn,
                appraisedBy=approval_section.appraisedBy,
                appraisedDate=datetime.strptime(
                    approval_section.appraisedDate, "%Y-%m-%d"
                ),
                recommendingApproval=approval_section.recommendingApproval,
                municipalityAssessorDate=datetime.strptime(
                    approval_section.municipalityAssessorDate, "%Y-%m-%d"
                ),
                approvedByProvince=approval_section.approvedByProvince,
                provincialAssessorDate=datetime.strptime(
                    approval_section.provincialAssessorDate, "%Y-%m-%d"
                ),
            )
            db.add(assessment)
            db.commit()
            db.refresh(assessment)
        except ValueError as date_error:
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail={"message": "Invalid date format", "error": str(date_error)},
            )
        except Exception as assessment_error:
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Failed to create assessment",
                    "error": str(assessment_error),
                },
            )

        # Return the combined response
        response = {
            "id": assessment.id,
            "owner_id": owner.id,
            "approval_section": {
                "tdn": assessment.tdn,
                "appraisedBy": assessment.appraisedBy,
                "appraisedDate": assessment.appraisedDate.strftime("%Y-%m-%d"),
                "recommendingApproval": assessment.recommendingApproval,
                "municipalityAssessorDate": assessment.municipalityAssessorDate.strftime(
                    "%Y-%m-%d"
                ),
                "approvedByProvince": assessment.approvedByProvince,
                "provincialAssessorDate": assessment.provincialAssessorDate.strftime(
                    "%Y-%m-%d"
                ),
            },
            "owner_details": {
                "id": owner.id,
                "owner": owner.owner,
                "ownerAddress": owner.ownerAddress,
                "admin_ben_user": owner.admin_ben_user,
                "transactionCode": owner.transactionCode,
                "pin": owner.pin,
                "tin": owner.tin,
                "telNo": owner.telNo,
                "td": owner.td,
            },
        }
        return response
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail={"message": "An unexpected error occurred", "error": str(e)},
        )


@router.get("/owners/", response_model=List[OwnerDetails])
async def get_all_owners(db: Session = Depends(get_db)):
    """
    Get all owners with their IDs in sequence
    """
    owners = db.query(OwnerDetailsModel).order_by(OwnerDetailsModel.id).all()
    return owners


# Example request for testing in your .rest file:
"""
POST http://localhost:8000/property-assessment/
Content-Type: application/json
Authorization: Bearer your-token-here

{
    "approval_section": {
        "tdn": "TDN2024-001",
        "appraisedBy": "John Doe",
        "appraisedDate": "2024-03-20",
        "recommendingApproval": "Jane Smith",
        "municipalityAssessorDate": "2024-03-21",
        "approvedByProvince": "Robert Johnson",
        "provincialAssessorDate": "2024-03-22"
    },
    "owner_details": {
        "owner": "John Doe",
        "ownerAddress": "123 Main St, City",
        "admin_ben_user": "Admin User",
        "transactionCode": "TRANS001",
        "pin": "1234567890",
        "tin": "123-456-789",
        "telNo": "+1234567890",
        "td": "TD2024-001"
    }
}
"""
