"""API endpoints for managing property assessments and owner details in the Real Property Tax Assessment System."""
from datetime import datetime
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from authentication.user_auth import verify_token
from database.database import get_db
from models import ApprovalSectionModel, OwnerDetailsModel
from schemas.assessment_schemas import CompleteAssessmentRequest, OwnerDetails

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> str:
    """Verify and return the current user from the JWT token.
    
    Args:
        token: The JWT token to verify.
        db: Database session.
    
    Returns:
        str: The username from the token.
        
    Raises:
        HTTPException: If the token is invalid.
    """
    username = verify_token(token)
    if username is None:
        raise HTTPException(status_code=401, detail='Invalid token')
    return username


@router.post('/add/', response_model=Dict)
async def create_property_assessment(
    request: CompleteAssessmentRequest,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
) -> Dict:
    try:
        # Create owner details
        owner = OwnerDetailsModel(
            owner=request.ownerDetails.owner,
            owner_address=request.ownerDetails.ownerAddress,
            admin_ben_user=request.ownerDetails.admin_ben_user,
            transaction_code=request.ownerDetails.transactionCode,
            pin=request.ownerDetails.pin,
            tin=request.ownerDetails.tin,
            tel_no=request.ownerDetails.telNo,
            td=request.ownerDetails.td,
        )
        db.add(owner)
        db.flush()

        # Create approval section
        assessment = ApprovalSectionModel(
            owner_id=owner.id,
            tdn=request.ownerDetails.td,
            appraised_by=request.approvalSection.appraisedBy,
            appraised_date=request.approvalSection.appraisedDate,
            recommending_approval=request.approvalSection.recommendingApproval,
            municipality_assessor_date=request.approvalSection.municipalityAssessorDate,
            approved_by_province=request.approvalSection.approvedByProvince,
            provincial_assessor_date=request.approvalSection.provincialAssessorDate,
        )
        db.add(assessment)
        db.commit()
        
        return {
            "status": "success",
            "message": "Assessment created successfully",
            "data": {
                "assessment_id": assessment.id,
                "owner_id": owner.id,
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail={'message': 'An unexpected error occurred', 'error': str(e)},
        )


@router.get('/owners/', response_model=List[OwnerDetails])
async def get_all_owners(db: Session = Depends(get_db)) -> List[OwnerDetails]:
    """Get all owners with their IDs in sequence.
    
    Args:
        db: Database session.
    
    Returns:
        List[OwnerDetails]: List of all owners ordered by ID.
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
        "appraised_by": "John Doe",
        "appraised_date": "2024-03-20",
        "recommending_approval": "Jane Smith",
        "municipality_assessor_date": "2024-03-21",
        "approved_by_province": "Robert Johnson",
        "provincial_assessor_date": "2024-03-22"
    },
    "owner_details": {
        "owner": "John Doe",
        "owner_address": "123 Main St, City",
        "admin_ben_user": "Admin User",
        "transaction_code": "TRANS001",
        "pin": "1234567890",
        "tin": "123-456-789",
        "tel_no": "+1234567890",
        "td": "TD2024-001"
    }
}
"""
