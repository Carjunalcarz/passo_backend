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


@router.post('/add', response_model=Dict)
async def create_flexible_assessment(
    request: dict,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
) -> Dict:
    """Create a building assessment with flexible data structure.
    
    This endpoint accepts any JSON structure and doesn't perform schema validation.
    Logs all created IDs on success.
    """
    # Track all created entities and their IDs
    created_ids = {}
    
    try:
        # 1. Create owner details
        owner = OwnerDetailsModel(
            owner=request.get("ownerDetails", {}).get("owner"),
            owner_address=request.get("ownerDetails", {}).get("ownerAddress"),
            admin_ben_user=request.get("ownerDetails", {}).get("admin_ben_user"),
            transaction_code=request.get("ownerDetails", {}).get("transactionCode"),
            pin=request.get("ownerDetails", {}).get("pin"),
            tin=request.get("ownerDetails", {}).get("tin"),
            tel_no=request.get("ownerDetails", {}).get("telNo"),
            td=request.get("ownerDetails", {}).get("td")
        )
        db.add(owner)
        db.flush()
        created_ids["owner_id"] = owner.id
        print(f"Created owner with ID: {owner.id}")
        
        try:
            # 2. Create approval section
            approval_section_data = {
                "owner_id": owner.id,
                "appraised_by": request.get("approvalSection", {}).get("appraisedBy"),
                "recommending_approval": request.get("approvalSection", {}).get("recommendingApproval"),
                "approved_by_province": request.get("approvalSection", {}).get("approvedByProvince")
            }
            
            # Handle date fields properly - convert empty strings to None
            appraised_date = request.get("approvalSection", {}).get("appraisedDate")
            municipality_date = request.get("approvalSection", {}).get("municipalityAssessorDate")
            provincial_date = request.get("approvalSection", {}).get("provincialAssessorDate")
            
            approval_section_data["appraised_date"] = None if not appraised_date else appraised_date
            approval_section_data["municipality_assessor_date"] = None if not municipality_date else municipality_date
            approval_section_data["provincial_assessor_date"] = None if not provincial_date else provincial_date
            
            approval = ApprovalSectionModel(**approval_section_data)
            db.add(approval)
            db.flush()
            created_ids["approval_section_id"] = approval.id
            print(f"Created approval section with ID: {approval.id}")
        except Exception as e:
            print(f"Error creating approval section: {str(e)}")
        
        try:
            # 3. Create land reference
            land_ref = LandReferenceModel(
                owner_id=owner.id,
                land_owner=request.get("landReference", {}).get("land_owner"),
                block_no=request.get("landReference", {}).get("block_no"),
                tdn_no=request.get("landReference", {}).get("tdn_no"),
                pin=request.get("landReference", {}).get("pin"),
                lot_no=request.get("landReference", {}).get("lot_no"),
                survey_no=request.get("landReference", {}).get("survey_no"),
                area=request.get("landReference", {}).get("area")
            )
            db.add(land_ref)
            db.flush()
            created_ids["land_reference_id"] = land_ref.id
            print(f"Created land reference with ID: {land_ref.id}")
        except Exception as e:
            print(f"Error creating land reference: {str(e)}")
        
        try:
            # 4. Create building assessment
            assessment = BuildingAssessmentModel(
                owner_id=owner.id,
                street=request.get("street", ""),
                address_municipality=request.get("address_municipality", ""),
                address_province=request.get("address_province", ""),
                address_barangay=request.get("address_barangay", ""),
                assessment_value=request.get("propertyAppraisal", {}).get("marketValue", 0) * 0.5,
                building_category=request.get("propertyAppraisal", {}).get("buildingType", ""),
                taxable_value=request.get("taxableValue", []),
                effectivity_of_assessment=request.get("effectivityOfAssessment", ""),
                assessment_level=request.get("assessmentLevel", 0.0),
                cct=request.get("cct", {}),
                floor_plan=request.get("floor_plan", []),
                additional_item=request.get("additionalItem", "")
            )
            db.add(assessment)
            db.flush()
            created_ids["building_assessment_id"] = assessment.id
            print(f"Created building assessment with ID: {assessment.id}")
            
            try:
                # 5. Create building location
                location = BuildingLocationModel(
                    assessment_id=assessment.id,
                    address_municipality=request.get("buildingLocation", {}).get("address_municipality", ""),
                    address_barangay=request.get("buildingLocation", {}).get("address_barangay", ""),
                    street=request.get("buildingLocation", {}).get("street", ""),
                    address_province=request.get("buildingLocation", {}).get("address_province", "")
                )
                db.add(location)
                db.flush()
                created_ids["building_location_id"] = location.id
                print(f"Created building location with ID: {location.id}")
            except Exception as e:
                print(f"Error creating building location: {str(e)}")
            
            try:
                # 6. Create general description
                gen_desc = GeneralDescriptionModel(
                    assessment_id=assessment.id,
                    building_permit_no=request.get("generalDescription", {}).get("building_permit_no", ""),
                    certificate_of_completion_issued_on=request.get("generalDescription", {}).get("certificate_of_completion_issued_on"),
                    certificate_of_occupancy_issued_on=request.get("generalDescription", {}).get("certificate_of_occupancy_issued_on"),
                    date_of_occupied=request.get("generalDescription", {}).get("date_of_occupied"),
                    bldg_age=request.get("generalDescription", {}).get("bldg_age", ""),
                    no_of_storeys=request.get("generalDescription", {}).get("no_of_storeys", ""),
                    area_of_1st_floor=request.get("generalDescription", {}).get("area_of_1st_floor", ""),
                    area_of_2nd_floor=request.get("generalDescription", {}).get("area_of_2nd_floor", ""),
                    area_of_3rd_floor=request.get("generalDescription", {}).get("area_of_3rd_floor", ""),
                    area_of_4th_floor=request.get("generalDescription", {}).get("area_of_4th_floor", ""),
                    total_floor_area=request.get("generalDescription", {}).get("total_floor_area", 0),
                    kind_of_bldg=request.get("generalDescription", {}).get("kind_of_bldg", ""),
                    structural_type=request.get("generalDescription", {}).get("structural_type", ""),
                    unit_value=request.get("generalDescription", {}).get("unitValue", 0)
                )
                db.add(gen_desc)
                db.flush()
                created_ids["general_description_id"] = gen_desc.id
                print(f"Created general description with ID: {gen_desc.id}")
            except Exception as e:
                print(f"Error creating general description: {str(e)}")
            
            try:
                # 7. Create property appraisal
                appraisal = PropertyAppraisalModel(
                    assessment_id=assessment.id,
                    building_type=request.get("propertyAppraisal", {}).get("buildingType", ""),
                    building_structure=request.get("propertyAppraisal", {}).get("buildingStructure", ""),
                    total_area=request.get("propertyAppraisal", {}).get("totalArea", 0),
                    unit_value=request.get("propertyAppraisal", {}).get("unitValue", 0),
                    smv=request.get("propertyAppraisal", {}).get("smv", 0),
                    base_market_value=request.get("propertyAppraisal", {}).get("baseMarketValue", 0),
                    depreciation=request.get("propertyAppraisal", {}).get("depreciation", 0),
                    market_value=request.get("propertyAppraisal", {}).get("marketValue", 0)
                )
                db.add(appraisal)
                db.flush()
                created_ids["property_appraisal_id"] = appraisal.id
                print(f"Created property appraisal with ID: {appraisal.id}")
            except Exception as e:
                print(f"Error creating property appraisal: {str(e)}")
            
            try:
                # 8. Create structural material
                struct_material = StructuralMaterialModel(
                    assessment_id=assessment.id,
                    material_data=request.get("structuralMaterial", {}),
                    truss_other=request.get("truss_other", "")
                )
                db.add(struct_material)
                db.flush()
                created_ids["structural_material_id"] = struct_material.id
                print(f"Created structural material with ID: {struct_material.id}")
            except Exception as e:
                print(f"Error creating structural material: {str(e)}")
            
            # 9. Create additional items
            add_item_ids = []
            try:
                for item in request.get("additionalItems", {}).get("items", []):
                    add_item = AdditionalItemModel(
                        assessment_id=assessment.id,
                        item_id=item.get("id"),
                        label=item.get("label", ""),
                        item_value=item.get("value", {}),
                        quantity=item.get("quantity", 0),
                        amount=item.get("amount", 0),
                        description=item.get("description", "")
                    )
                    db.add(add_item)
                    db.flush()
                    add_item_ids.append(add_item.id)
                    print(f"Created additional item with ID: {add_item.id}")
                
                if add_item_ids:
                    created_ids["additional_item_ids"] = add_item_ids
            except Exception as e:
                print(f"Error creating additional items: {str(e)}")
            
            try:
                # 10. Create additional items summary
                add_summary = AdditionalItemsSummaryModel(
                    assessment_id=assessment.id,
                    total=request.get("additionalItems", {}).get("total", 0),
                    sub_total=request.get("additionalItems", {}).get("subTotal", 0)
                )
                db.add(add_summary)
                db.flush()
                created_ids["additional_items_summary_id"] = add_summary.id
                print(f"Created additional items summary with ID: {add_summary.id}")
            except Exception as e:
                print(f"Error creating additional items summary: {str(e)}")
            
            # 11. Create property assessment items
            prop_assess_item_ids = []
            try:
                # If propertyAssessment is missing, create a default entry
                if "propertyAssessment" not in request or "items" not in request.get("propertyAssessment", {}):
                    assess_item = PropertyAssessmentItemModel(
                        assessment_id=assessment.id,
                        item_id="default",
                        area=request.get("propertyAppraisal", {}).get("totalArea", 0),
                        unit_value=request.get("propertyAppraisal", {}).get("unitValue", 0),
                        smv=request.get("propertyAppraisal", {}).get("smv", 0),
                        base_market_value=request.get("propertyAppraisal", {}).get("baseMarketValue", 0),
                        depreciation_percentage=0,
                        depreciator_cost=0,
                        market_value=request.get("propertyAppraisal", {}).get("marketValue", 0),
                        building_category=request.get("propertyAppraisal", {}).get("buildingType", "")
                    )
                    db.add(assess_item)
                    db.flush()
                    prop_assess_item_ids.append(assess_item.id)
                    print(f"Created default property assessment item with ID: {assess_item.id}")
                else:
                    for item in request.get("propertyAssessment", {}).get("items", []):
                        assess_item = PropertyAssessmentItemModel(
                            assessment_id=assessment.id,
                            item_id=item.get("id", ""),
                            area=item.get("area", 0),
                            unit_value=item.get("unitValue", 0),
                            smv=item.get("smv", 0),
                            base_market_value=item.get("baseMarketValue", 0),
                            depreciation_percentage=item.get("depreciationPercentage", 0),
                            depreciator_cost=item.get("depreciatorCost", 0),
                            market_value=item.get("marketValue", 0),
                            building_category=item.get("buildingCategory", "")
                        )
                        db.add(assess_item)
                        db.flush()
                        prop_assess_item_ids.append(assess_item.id)
                        print(f"Created property assessment item with ID: {assess_item.id}")
                
                if prop_assess_item_ids:
                    created_ids["property_assessment_item_ids"] = prop_assess_item_ids
            except Exception as e:
                print(f"Error creating property assessment items: {str(e)}")
            
            # 12. Create memoranda
            memo_ids = []
            try:
                for memo in request.get("memoranda", []):
                    if memo.get("date") or memo.get("details"):  # Create if either field is present
                        memorandum = MemorandumModel(
                            assessment_id=assessment.id,
                            date=memo.get("date"),
                            details=memo.get("details", "")
                        )
                        db.add(memorandum)
                        db.flush()
                        memo_ids.append(memorandum.id)
                        print(f"Created memorandum with ID: {memorandum.id}")
                
                if memo_ids:
                    created_ids["memorandum_ids"] = memo_ids
            except Exception as e:
                print(f"Error creating memoranda: {str(e)}")
            
            # 13. Create superseded records
            superseded_ids = []
            try:
                for record in request.get("recordOfSupersededAssessment", {}).get("records", []):
                    superseded = SupersededRecordModel(
                        assessment_id=assessment.id,
                        pin=record.get("pin", ""),
                        td_arp_no=record.get("tdArpNo", ""),
                        total_assessed_value=record.get("totalAssessedValue", ""),
                        previous_owner=record.get("previousOwner", ""),
                        date_of_effectivity=record.get("dateOfEffectivity"),
                        record_date=record.get("date"),
                        assessment=record.get("assessment", ""),
                        tax_mapping=record.get("taxMapping", ""),
                        records=record.get("records", "")
                    )
                    db.add(superseded)
                    db.flush()
                    superseded_ids.append(superseded.id)
                    print(f"Created superseded record with ID: {superseded.id}")
                
                if superseded_ids:
                    created_ids["superseded_record_ids"] = superseded_ids
            except Exception as e:
                print(f"Error creating superseded records: {str(e)}")
        
        except Exception as e:
            print(f"Error in building assessment related records: {str(e)}")
        
        # Commit all changes to the database
        db.commit()
        print("All changes committed successfully")
        
        # Log all IDs to console
        print("Created IDs summary:")
        for key, value in created_ids.items():
            print(f"  {key}: {value}")
        
        return {
            "status": "success",
            "message": "Assessment data saved successfully",
            "data": created_ids
        }
        
    except Exception as e:
        db.rollback()
        print(f"Transaction rolled back due to error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={'message': 'An error occurred while creating the assessment', 'error': str(e)}
        )

