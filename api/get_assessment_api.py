"""API endpoints for managing property assessments and owner details in the Real Property Tax Assessment System."""
from datetime import datetime
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from authentication.user_auth import verify_token
from database.database import get_db
from models import ApprovalSectionModel, OwnerDetailsModel, LandReferenceModel, BuildingLocationModel, GeneralDescriptionModel, PropertyAppraisalModel, AdditionalItemModel, AdditionalItemsSummaryModel, PropertyAssessmentItemModel, MemorandumModel, SupersededRecordModel, StructuralMaterialModel, BuildingAssessmentModel
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


@router.get('/get-assessments/', response_model=List[Dict])
async def get_all_assessments(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
) -> List[Dict]:
    """Retrieve all assessments with their complete data.
    
    Returns:
        List[Dict]: List of all assessments with nested related data.
    """
    try:
        # Query for all owners (starting point)
        owners = db.query(OwnerDetailsModel).all()
        
        result = []
        for owner in owners:
            # Get the assessment for this owner
            assessment = db.query(BuildingAssessmentModel).filter(
                BuildingAssessmentModel.owner_id == owner.id
            ).first()
            
            owner_data = {
                "id": owner.id,
                "owner": owner.owner,
                "owner_address": owner.owner_address,
                "admin_ben_user": owner.admin_ben_user,
                "transaction_code": owner.transaction_code,
                "pin": owner.pin,
                "tin": owner.tin,
                "tel_no": owner.tel_no,
                "td": owner.td
            }
            
            # Get approval section
            approval = db.query(ApprovalSectionModel).filter(
                ApprovalSectionModel.owner_id == owner.id
            ).first()
            
            approval_data = None
            if approval:
                approval_data = {
                    "id": approval.id,
                    "appraised_by": approval.appraised_by,
                    "appraised_date": approval.appraised_date,
                    "recommending_approval": approval.recommending_approval,
                    "municipality_assessor_date": approval.municipality_assessor_date,
                    "approved_by_province": approval.approved_by_province,
                    "provincial_assessor_date": approval.provincial_assessor_date
                }
            
            # Get land reference
            land_ref = db.query(LandReferenceModel).filter(
                LandReferenceModel.owner_id == owner.id
            ).first()
            
            land_data = None
            if land_ref:
                land_data = {
                    "id": land_ref.id,
                    "land_owner": land_ref.land_owner,
                    "block_no": land_ref.block_no,
                    "tdn_no": land_ref.tdn_no,
                    "pin": land_ref.pin,
                    "lot_no": land_ref.lot_no,
                    "survey_no": land_ref.survey_no,
                    "area": land_ref.area
                }
            
            assessment_data = None
            if assessment:
                # Get building location
                location = db.query(BuildingLocationModel).filter(
                    BuildingLocationModel.assessment_id == assessment.id
                ).first()
                
                location_data = None
                if location:
                    location_data = {
                        "id": location.id,
                        "address_municipality": location.address_municipality,
                        "address_barangay": location.address_barangay,
                        "street": location.street,
                        "address_province": location.address_province
                    }
                
                # Get general description
                gen_desc = db.query(GeneralDescriptionModel).filter(
                    GeneralDescriptionModel.assessment_id == assessment.id
                ).first()
                
                gen_desc_data = None
                if gen_desc:
                    gen_desc_data = {
                        "id": gen_desc.id,
                        "building_permit_no": gen_desc.building_permit_no,
                        "certificate_of_completion_issued_on": gen_desc.certificate_of_completion_issued_on,
                        "certificate_of_occupancy_issued_on": gen_desc.certificate_of_occupancy_issued_on,
                        "date_of_occupied": gen_desc.date_of_occupied,
                        "bldg_age": gen_desc.bldg_age,
                        "no_of_storeys": gen_desc.no_of_storeys,
                        "area_of_1st_floor": gen_desc.area_of_1st_floor,
                        "area_of_2nd_floor": gen_desc.area_of_2nd_floor,
                        "area_of_3rd_floor": gen_desc.area_of_3rd_floor,
                        "area_of_4th_floor": gen_desc.area_of_4th_floor,
                        "total_floor_area": gen_desc.total_floor_area,
                        "kind_of_bldg": gen_desc.kind_of_bldg,
                        "structural_type": gen_desc.structural_type,
                        "unit_value": gen_desc.unit_value
                    }
                
                # Get property appraisal
                appraisal = db.query(PropertyAppraisalModel).filter(
                    PropertyAppraisalModel.assessment_id == assessment.id
                ).first()
                
                appraisal_data = None
                if appraisal:
                    appraisal_data = {
                        "id": appraisal.id,
                        "building_type": appraisal.building_type,
                        "building_structure": appraisal.building_structure,
                        "total_area": appraisal.total_area,
                        "unit_value": appraisal.unit_value,
                        "smv": appraisal.smv,
                        "base_market_value": appraisal.base_market_value,
                        "depreciation": appraisal.depreciation,
                        "market_value": appraisal.market_value
                    }
                
                # Get structural material
                struct_material = db.query(StructuralMaterialModel).filter(
                    StructuralMaterialModel.assessment_id == assessment.id
                ).first()
                
                struct_material_data = None
                if struct_material:
                    struct_material_data = {
                        "id": struct_material.id,
                        "material_data": struct_material.material_data,
                        "truss_other": struct_material.truss_other
                    }
                
                # Get additional items
                add_items = db.query(AdditionalItemModel).filter(
                    AdditionalItemModel.assessment_id == assessment.id
                ).all()
                
                add_items_data = []
                for item in add_items:
                    add_items_data.append({
                        "id": item.id,
                        "item_id": item.item_id,
                        "label": item.label,
                        "item_value": item.item_value,
                        "quantity": item.quantity,
                        "amount": item.amount,
                        "description": item.description
                    })
                
                # Get additional items summary
                add_summary = db.query(AdditionalItemsSummaryModel).filter(
                    AdditionalItemsSummaryModel.assessment_id == assessment.id
                ).first()
                
                add_summary_data = None
                if add_summary:
                    add_summary_data = {
                        "id": add_summary.id,
                        "total": add_summary.total,
                        "sub_total": add_summary.sub_total
                    }
                
                # Get property assessment items
                assess_items = db.query(PropertyAssessmentItemModel).filter(
                    PropertyAssessmentItemModel.assessment_id == assessment.id
                ).all()
                
                assess_items_data = []
                for item in assess_items:
                    assess_items_data.append({
                        "id": item.id,
                        "item_id": item.item_id,
                        "area": item.area,
                        "unit_value": item.unit_value,
                        "smv": item.smv,
                        "base_market_value": item.base_market_value,
                        "depreciation_percentage": item.depreciation_percentage,
                        "depreciator_cost": item.depreciator_cost,
                        "market_value": item.market_value,
                        "building_category": item.building_category
                    })
                
                # Get memoranda
                memoranda = db.query(MemorandumModel).filter(
                    MemorandumModel.assessment_id == assessment.id
                ).all()
                
                memoranda_data = []
                for memo in memoranda:
                    memoranda_data.append({
                        "id": memo.id,
                        "date": memo.date,
                        "details": memo.details
                    })
                
                # Get superseded records
                superseded = db.query(SupersededRecordModel).filter(
                    SupersededRecordModel.assessment_id == assessment.id
                ).all()
                
                superseded_data = []
                for record in superseded:
                    superseded_data.append({
                        "id": record.id,
                        "pin": record.pin,
                        "td_arp_no": record.td_arp_no,
                        "total_assessed_value": record.total_assessed_value,
                        "previous_owner": record.previous_owner,
                        "date_of_effectivity": record.date_of_effectivity,
                        "record_date": record.record_date,
                        "assessment": record.assessment,
                        "tax_mapping": record.tax_mapping,
                        "records": record.records
                    })
                
                # Combine all assessment data
                assessment_data = {
                    "id": assessment.id,
                    "street": assessment.street,
                    "address_municipality": assessment.address_municipality,
                    "address_province": assessment.address_province,
                    "address_barangay": assessment.address_barangay,
                    "assessment_value": assessment.assessment_value,
                    "building_category": assessment.building_category,
                    "taxable_value": assessment.taxable_value,
                    "effectivity_of_assessment": assessment.effectivity_of_assessment,
                    "assessment_level": assessment.assessment_level,
                    "cct": assessment.cct,
                    "floor_plan": assessment.floor_plan,
                    "additional_item": assessment.additional_item,
                    "building_location": location_data,
                    "general_description": gen_desc_data,
                    "property_appraisal": appraisal_data,
                    "structural_material": struct_material_data,
                    "additional_items": add_items_data,
                    "additional_items_summary": add_summary_data,
                    "property_assessment_items": assess_items_data,
                    "memoranda": memoranda_data,
                    "superseded_records": superseded_data
                }
            
            # Build the complete assessment record
            complete_assessment = {
                "owner_details": owner_data,
                "approval_section": approval_data,
                "land_reference": land_data,
                "building_assessment": assessment_data
            }
            
            result.append(complete_assessment)
        
        return result
        
    except Exception as e:
        print(f"Error retrieving assessments: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={'message': 'An error occurred while retrieving assessments', 'error': str(e)}
        )


@router.get('/get-assessment/{owner_id}', response_model=Dict)
async def get_assessment_by_owner_id(
    owner_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
) -> Dict:
    """Retrieve a complete assessment by owner ID.
    
    Args:
        owner_id: The ID of the owner to retrieve the assessment for.
        
    Returns:
        Dict: The complete assessment data with all related information.
    """
    try:
        # Get the owner
        owner = db.query(OwnerDetailsModel).filter(OwnerDetailsModel.id == owner_id).first()
        
        if not owner:
            raise HTTPException(status_code=404, detail=f"Owner with ID {owner_id} not found")
        
        owner_data = {
            "id": owner.id,
            "owner": owner.owner,
            "owner_address": owner.owner_address,
            "admin_ben_user": owner.admin_ben_user,
            "transaction_code": owner.transaction_code,
            "pin": owner.pin,
            "tin": owner.tin,
            "tel_no": owner.tel_no,
            "td": owner.td
        }
        
        # Get approval section
        approval = db.query(ApprovalSectionModel).filter(
            ApprovalSectionModel.owner_id == owner.id
        ).first()
        
        approval_data = None
        if approval:
            approval_data = {
                "id": approval.id,
                "appraised_by": approval.appraised_by,
                "appraised_date": approval.appraised_date,
                "recommending_approval": approval.recommending_approval,
                "municipality_assessor_date": approval.municipality_assessor_date,
                "approved_by_province": approval.approved_by_province,
                "provincial_assessor_date": approval.provincial_assessor_date
            }
        
        # Get land reference
        land_ref = db.query(LandReferenceModel).filter(
            LandReferenceModel.owner_id == owner.id
        ).first()
        
        land_data = None
        if land_ref:
            land_data = {
                "id": land_ref.id,
                "land_owner": land_ref.land_owner,
                "block_no": land_ref.block_no,
                "tdn_no": land_ref.tdn_no,
                "pin": land_ref.pin,
                "lot_no": land_ref.lot_no,
                "survey_no": land_ref.survey_no,
                "area": land_ref.area
            }
        
        # Get the assessment
        assessment = db.query(BuildingAssessmentModel).filter(
            BuildingAssessmentModel.owner_id == owner.id
        ).first()
        
        assessment_data = None
        if assessment:
            # Get building location
            location = db.query(BuildingLocationModel).filter(
                BuildingLocationModel.assessment_id == assessment.id
            ).first()
            
            location_data = None
            if location:
                location_data = {
                    "id": location.id,
                    "address_municipality": location.address_municipality,
                    "address_barangay": location.address_barangay,
                    "street": location.street,
                    "address_province": location.address_province
                }
            
            # Get general description
            gen_desc = db.query(GeneralDescriptionModel).filter(
                GeneralDescriptionModel.assessment_id == assessment.id
            ).first()
            
            gen_desc_data = None
            if gen_desc:
                gen_desc_data = {
                    "id": gen_desc.id,
                    "building_permit_no": gen_desc.building_permit_no,
                    "certificate_of_completion_issued_on": gen_desc.certificate_of_completion_issued_on,
                    "certificate_of_occupancy_issued_on": gen_desc.certificate_of_occupancy_issued_on,
                    "date_of_occupied": gen_desc.date_of_occupied,
                    "bldg_age": gen_desc.bldg_age,
                    "no_of_storeys": gen_desc.no_of_storeys,
                    "area_of_1st_floor": gen_desc.area_of_1st_floor,
                    "area_of_2nd_floor": gen_desc.area_of_2nd_floor,
                    "area_of_3rd_floor": gen_desc.area_of_3rd_floor,
                    "area_of_4th_floor": gen_desc.area_of_4th_floor,
                    "total_floor_area": gen_desc.total_floor_area,
                    "kind_of_bldg": gen_desc.kind_of_bldg,
                    "structural_type": gen_desc.structural_type,
                    "unit_value": gen_desc.unit_value
                }
            
            # Get property appraisal
            appraisal = db.query(PropertyAppraisalModel).filter(
                PropertyAppraisalModel.assessment_id == assessment.id
            ).first()
            
            appraisal_data = None
            if appraisal:
                appraisal_data = {
                    "id": appraisal.id,
                    "building_type": appraisal.building_type,
                    "building_structure": appraisal.building_structure,
                    "total_area": appraisal.total_area,
                    "unit_value": appraisal.unit_value,
                    "smv": appraisal.smv,
                    "base_market_value": appraisal.base_market_value,
                    "depreciation": appraisal.depreciation,
                    "market_value": appraisal.market_value
                }
            
            # Get structural material
            struct_material = db.query(StructuralMaterialModel).filter(
                StructuralMaterialModel.assessment_id == assessment.id
            ).first()
            
            struct_material_data = None
            if struct_material:
                struct_material_data = {
                    "id": struct_material.id,
                    "material_data": struct_material.material_data,
                    "truss_other": struct_material.truss_other
                }
            
            # Get additional items
            add_items = db.query(AdditionalItemModel).filter(
                AdditionalItemModel.assessment_id == assessment.id
            ).all()
            
            add_items_data = []
            for item in add_items:
                add_items_data.append({
                    "id": item.id,
                    "item_id": item.item_id,
                    "label": item.label,
                    "item_value": item.item_value,
                    "quantity": item.quantity,
                    "amount": item.amount,
                    "description": item.description
                })
            
            # Get additional items summary
            add_summary = db.query(AdditionalItemsSummaryModel).filter(
                AdditionalItemsSummaryModel.assessment_id == assessment.id
            ).first()
            
            add_summary_data = None
            if add_summary:
                add_summary_data = {
                    "id": add_summary.id,
                    "total": add_summary.total,
                    "sub_total": add_summary.sub_total
                }
            
            # Get property assessment items
            assess_items = db.query(PropertyAssessmentItemModel).filter(
                PropertyAssessmentItemModel.assessment_id == assessment.id
            ).all()
            
            assess_items_data = []
            for item in assess_items:
                assess_items_data.append({
                    "id": item.id,
                    "item_id": item.item_id,
                    "area": item.area,
                    "unit_value": item.unit_value,
                    "smv": item.smv,
                    "base_market_value": item.base_market_value,
                    "depreciation_percentage": item.depreciation_percentage,
                    "depreciator_cost": item.depreciator_cost,
                    "market_value": item.market_value,
                    "building_category": item.building_category
                })
            
            # Get memoranda
            memoranda = db.query(MemorandumModel).filter(
                MemorandumModel.assessment_id == assessment.id
            ).all()
            
            memoranda_data = []
            for memo in memoranda:
                memoranda_data.append({
                    "id": memo.id,
                    "date": memo.date,
                    "details": memo.details
                })
            
            # Get superseded records
            superseded = db.query(SupersededRecordModel).filter(
                SupersededRecordModel.assessment_id == assessment.id
            ).all()
            
            superseded_data = []
            for record in superseded:
                superseded_data.append({
                    "id": record.id,
                    "pin": record.pin,
                    "td_arp_no": record.td_arp_no,
                    "total_assessed_value": record.total_assessed_value,
                    "previous_owner": record.previous_owner,
                    "date_of_effectivity": record.date_of_effectivity,
                    "record_date": record.record_date,
                    "assessment": record.assessment,
                    "tax_mapping": record.tax_mapping,
                    "records": record.records
                })
            
            # Combine all assessment data
            assessment_data = {
                "id": assessment.id,
                "street": assessment.street,
                "address_municipality": assessment.address_municipality,
                "address_province": assessment.address_province,
                "address_barangay": assessment.address_barangay,
                "assessment_value": assessment.assessment_value,
                "building_category": assessment.building_category,
                "taxable_value": assessment.taxable_value,
                "effectivity_of_assessment": assessment.effectivity_of_assessment,
                "assessment_level": assessment.assessment_level,
                "cct": assessment.cct,
                "floor_plan": assessment.floor_plan,
                "additional_item": assessment.additional_item,
                "building_location": location_data,
                "general_description": gen_desc_data,
                "property_appraisal": appraisal_data,
                "structural_material": struct_material_data,
                "additional_items": add_items_data,
                "additional_items_summary": add_summary_data,
                "property_assessment_items": assess_items_data,
                "memoranda": memoranda_data,
                "superseded_records": superseded_data
            }
        
        # Build the complete assessment record
        complete_assessment = {
            "owner_details": owner_data,
            "approval_section": approval_data,
            "land_reference": land_data,
            "building_assessment": assessment_data
        }
        
        return complete_assessment
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error retrieving assessment: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={'message': 'An error occurred while retrieving the assessment', 'error': str(e)}
        )