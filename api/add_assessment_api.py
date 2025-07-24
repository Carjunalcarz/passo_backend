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
import os
import io
import base64
import uuid
from ftplib import FTP, FTP_TLS, error_perm, error_temp
import json
import traceback
import ssl
import imghdr

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


class MyFTP_TLS(FTP_TLS):
    """
    A custom FTP_TLS class that overrides the storbinary method to handle
    ConnectionResetError during the data connection's TLS shutdown. This can
    occur with some FTP servers that close the data connection abruptly after
    the file is transferred.
    """
    def storbinary(self, cmd, fp, blocksize=8192, callback=None, rest=None):
        self.voidcmd('TYPE I')
        with self.transfercmd(cmd, rest) as conn:
            while True:
                buf = fp.read(blocksize)
                if not buf:
                    break
                conn.sendall(buf)
                if callback:
                    callback(buf)
            # Shutdown the TLS layer on the data connection
            if isinstance(conn, ssl.SSLSocket):
                try:
                    conn.unwrap()
                except ConnectionResetError:
                    # Ignore the error that can be caused by the server
                    # closing the data connection abruptly.
                    pass
        try:
            return self.voidresp()
        except error_temp as e:
            # Some FTP servers may send this error after a successful transfer
            # when they have issues with TLS session resumption on the data connection.
            if "TLS session of data connection not resumed" in str(e):
                # The file is likely transferred, so we can ignore this error.
                return "226 Transfer complete (error ignored)."
            raise


def upload_image_to_ftp(base64_str, owner=None):
    FTP_HOST = "192.168.1.106"
    FTP_USER = "ajncarz"
    FTP_PASS = "12345"
    FTP_DIR = "/PASSO"
    FTP_URL_BASE = "http://192.168.1.106/PASSO"
    Year = datetime.now().year
    Month = datetime.now().month
    Day = datetime.now().day

    print("Base64 string (first 100 chars):", base64_str[:100])
    print("Starting FTP upload...")
    # Remove data:image/...;base64, if present
    if ',' in base64_str:
        base64_str = base64_str.split(',')[1]
    print("Decoding base64...")
    image_data = base64.b64decode(base64_str)
    image_type = imghdr.what(None, h=image_data)
    if image_type is None:
        image_type = 'png'
    filename = f"{uuid.uuid4().hex}.{image_type}"

    # Build the full directory path
    dir_parts = ["/PASSO", str(Year), str(Month), str(Day)]
    if owner:
        owner_dir = "".join(c for c in str(owner) if c.isalnum() or c in (' ', '_', '-')).rstrip()
        dir_parts.append(owner_dir)
    else:
        owner_dir = None
    full_dir = "/".join(dir_parts)

    print("Connecting to FTP...")
    with FTP(FTP_HOST) as ftp:
        ftp.login(FTP_USER, FTP_PASS)
        print("Logged in.")
        # Create each part of the directory if it doesn't exist
        path_so_far = ""
        for part in dir_parts:
            path_so_far = f"{path_so_far}/{part}".replace("//", "/")
            try:
                ftp.mkd(path_so_far)
            except Exception:
                pass  # Directory may already exist
        ftp.cwd(full_dir)
        print("Changed directory.")
        ftp.storbinary(f"STOR {filename}", io.BytesIO(image_data))
        print("Upload complete.")
    # Return the path including the owner directory if used
    return f"{Year}/{Month}/{Day}/{owner_dir}/{filename}" if owner_dir else f"{Year}/{Month}/{Day}/{filename}"

def upload_images_and_get_urls(image_list, owner=None):
    # If the list contains dicts with 'data_url', extract the value
    return [upload_image_to_ftp(img['data_url'] if isinstance(img, dict) and 'data_url' in img else img, owner) for img in image_list]



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
        mun_code = request.get("buildingLocation", {}).get("mun_code")
        bcode = request.get("buildingLocation", {}).get("bcode")
        td_value = mun_code + "-" + bcode
        owner = OwnerDetailsModel(
            owner=request.get("ownerDetails", {}).get("owner"),
            owner_address=request.get("ownerDetails", {}).get("ownerAddress"),
            admin_ben_user=request.get("ownerDetails", {}).get("admin_ben_user"),
            admin_ben_user_address=request.get("ownerDetails", {}).get("admin_ben_user_address"),
            transaction_code=request.get("ownerDetails", {}).get("transactionCode"),
            pin=request.get("ownerDetails", {}).get("pin"),
            tin=request.get("ownerDetails", {}).get("tin"),
            tel_no=request.get("ownerDetails", {}).get("telNo"),
            td=td_value,  # Temporary, will update after flush
            image_list=json.dumps(upload_images_and_get_urls(request.get("ownerDetails", {}).get("image_list", []), request.get("ownerDetails", {}).get("owner")))
        )
        db.add(owner)
        db.flush()  # Now owner.id is available

        # Replace last digit of td_value with owner.id
        if td_value and owner.id is not None:
            # If td_value is a string and owner.id is an int
            td_new = td_value +"-"+ str(owner.id)
            owner.td = td_new
            db.flush()  # Update the value in the database

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
            # Convert effectivity_of_assessment dict to string if it's a dict
            effectivity_data = request.get("effectivityOfAssessment", "")
            if isinstance(effectivity_data, dict):
                # Convert dict to a readable string format
                effectivity_str = f"{effectivity_data.get('quarter', '')} {effectivity_data.get('year', '')}".strip()
            else:
                effectivity_str = str(effectivity_data) if effectivity_data else ""

            assessment = BuildingAssessmentModel(
                owner_id=owner.id,
                street=request.get("street", ""),
                address_municipality=request.get("address_municipality", ""),
                address_province=request.get("address_province", ""),
                address_barangay=request.get("address_barangay", ""),
                assessment_value=request.get("propertyAppraisal", {}).get("marketValue", 0) * 0.5,
                building_category=request.get("propertyAppraisal", {}).get("buildingType", ""),
                taxable_value=request.get("taxableValue", []),
                effectivity_of_assessment=effectivity_str,  # Use the converted string
                assessment_level=request.get("assessmentLevel", 0.0),
                cct=request.get("cct", {}),
                floor_plan=request.get("floor_plan", []),
                additional_item=request.get("additionalItem", ""),
                image_list=request.get("buildingLocation", {}).get("image_list", [])
            )
            db.add(assessment)
            db.flush()
            created_ids["building_assessment_id"] = assessment.id
            print(f"Created building assessment with ID: {assessment.id}")
            
            try:
                # 5. Create building location
            

                # If your DB field is Text, use json.dumps
                location = BuildingLocationModel(
                    assessment_id=assessment.id,
                    address_municipality=request.get("buildingLocation", {}).get("address_municipality", ""),
                    address_barangay=request.get("buildingLocation", {}).get("address_barangay", ""),
                    street=request.get("buildingLocation", {}).get("street", ""),
                    address_province=request.get("buildingLocation", {}).get("address_province", ""),
                    bcode=request.get("buildingLocation", {}).get("bcode", ""),
                    mun_code=request.get("buildingLocation", {}).get("mun_code", ""),
                    image_list=json.dumps(upload_images_and_get_urls(request.get("buildingLocation", {}).get("image_list", []), owner.owner))  # Use json.dumps if field is Text
                )
                db.add(location)
                db.flush()
                created_ids["building_location_id"] = location.id
                print(f"Created building location with ID: {location.id}")
            except Exception as e:
                import traceback
                print(f"Error creating building location: {str(e)}")
                traceback.print_exc()
                raise HTTPException(status_code=500, detail=f"Building location error: {str(e)}")
            
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
                    unit_value=request.get("generalDescription", {}).get("unitValue", 0),
                    cct_image=json.dumps(upload_images_and_get_urls(request.get("generalDescription", {}).get("cct_image", []), owner.owner)),
                    floor_plan_image=json.dumps(upload_images_and_get_urls(request.get("generalDescription", {}).get("floor_plan_image", []), owner.owner))
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
                    # Convert effectivity_of_assessment dict to string if it's a dict
                    effectivity_data = request.get("propertyAssessment", {}).get("effectivityOfAssessment", "")
                    if isinstance(effectivity_data, dict):
                        # Convert dict to a readable string format
                        effectivity_str = f"{effectivity_data.get('quarter', '')} {effectivity_data.get('year', '')}".strip()
                    else:
                        effectivity_str = str(effectivity_data) if effectivity_data else ""
                        
                    assess_item = PropertyAssessmentItemModel(
                        assessment_id=assessment.id,
                        assessment_level=request.get("propertyAssessment", {}).get("assessment_level", ""),
                        assessment_value=request.get("propertyAssessment", {}).get("assessment_value", 0),
                        total_area=request.get("propertyAssessment", {}).get("total_area", 0),
                        market_value=request.get("propertyAssessment", {}).get("market_value", 0),
                        building_category=request.get("propertyAssessment", {}).get("building_category", ""),
                        taxable=1 if request.get("propertyAssessment", {}).get("taxable", False) else 0,
                        eff_year=request.get("propertyAssessment", {}).get("eff_year", ""),
                        eff_quarter=request.get("propertyAssessment", {}).get("eff_quarter", "")
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


@router.put('/update', response_model=Dict)
async def update_flexible_assessment(
    request: dict,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
) -> Dict:
    """
    Update an existing assessment and all related records using their IDs.
    """
    try:
        updated_ids = {}

        # 1. Update Owner Details
        owner_data = request.get("ownerDetails", {})
        owner_id = owner_data.get("owner_id")
        if owner_id:
            owner = db.query(OwnerDetailsModel).filter_by(id=owner_id).first()
            if owner:
                owner.owner = owner_data.get("owner", owner.owner)
                owner.owner_address = owner_data.get("ownerAddress", owner.owner_address)
                owner.admin_ben_user = owner_data.get("admin_ben_user", owner.admin_ben_user)
                owner.admin_ben_user_address = owner_data.get("admin_ben_user_address", owner.admin_ben_user_address)
                owner.transaction_code = owner_data.get("transactionCode", owner.transaction_code)
                owner.pin = owner_data.get("pin", owner.pin)
                owner.tin = owner_data.get("tin", owner.tin)
                owner.tel_no = owner_data.get("telNo", owner.tel_no)
                owner.td = owner_data.get("td", owner.td)
                owner.image_list = json.dumps(upload_images_and_get_urls(owner_data.get("image_list", []), owner.owner))
                db.flush()
                updated_ids["owner_id"] = owner.id

        # 2. Update Approval Section
        approval_data = request.get("approvalSection", {})
        approval_section_id = approval_data.get("approval_section_id")
        if approval_section_id:
            approval = db.query(ApprovalSectionModel).filter_by(id=approval_section_id).first()
            if approval:
                approval.appraised_by = approval_data.get("appraisedBy", approval.appraised_by)
                approval.recommending_approval = approval_data.get("recommendingApproval", approval.recommending_approval)
                approval.approved_by_province = approval_data.get("approvedByProvince", approval.approved_by_province)
                approval.appraised_date = approval_data.get("appraisedDate", approval.appraised_date)
                approval.municipality_assessor_date = approval_data.get("municipalityAssessorDate", approval.municipality_assessor_date)
                approval.provincial_assessor_date = approval_data.get("provincialAssessorDate", approval.provincial_assessor_date)
                db.flush()
                updated_ids["approval_section_id"] = approval.id

        # 3. Update Land Reference
        land_ref_data = request.get("landReference", {})
        land_reference_id = land_ref_data.get("land_reference_id")
        if land_reference_id:
            land_ref = db.query(LandReferenceModel).filter_by(id=land_reference_id).first()
            if land_ref:
                land_ref.land_owner = land_ref_data.get("land_owner", land_ref.land_owner)
                land_ref.block_no = land_ref_data.get("block_no", land_ref.block_no)
                land_ref.tdn_no = land_ref_data.get("tdn_no", land_ref.tdn_no)
                land_ref.pin = land_ref_data.get("pin", land_ref.pin)
                land_ref.lot_no = land_ref_data.get("lot_no", land_ref.lot_no)
                land_ref.survey_no = land_ref_data.get("survey_no", land_ref.survey_no)
                land_ref.area = land_ref_data.get("area", land_ref.area)
                db.flush()
                updated_ids["land_reference_id"] = land_ref.id

        # 4. Update Building Assessment
        assessment_id = request.get("building_assessment_id")
        if assessment_id:
            assessment = db.query(BuildingAssessmentModel).filter_by(id=assessment_id).first()
            if assessment:
                assessment.street = request.get("street", assessment.street)
                assessment.address_municipality = request.get("address_municipality", assessment.address_municipality)
                assessment.address_province = request.get("address_province", assessment.address_province)
                assessment.address_barangay = request.get("address_barangay", assessment.address_barangay)
                assessment.assessment_value = request.get("propertyAppraisal", {}).get("marketValue", assessment.assessment_value)
                assessment.building_category = request.get("propertyAppraisal", {}).get("buildingType", assessment.building_category)
                assessment.taxable_value = request.get("taxableValue", assessment.taxable_value)
                effectivity_data = request.get("effectivityOfAssessment", "")
                if isinstance(effectivity_data, dict):
                    effectivity_str = f"{effectivity_data.get('quarter', '')} {effectivity_data.get('year', '')}".strip()
                else:
                    effectivity_str = str(effectivity_data) if effectivity_data else assessment.effectivity_of_assessment
                assessment.effectivity_of_assessment = effectivity_str
                assessment.assessment_level = request.get("assessmentLevel", assessment.assessment_level)
                assessment.cct = request.get("cct", assessment.cct)
                assessment.floor_plan = request.get("floor_plan", assessment.floor_plan)
                assessment.additional_item = request.get("additionalItem", assessment.additional_item)
                assessment.image_list = request.get("buildingLocation", {}).get("image_list", assessment.image_list)
                db.flush()
                updated_ids["building_assessment_id"] = assessment.id

                # 5. Update Building Location
                location_data = request.get("buildingLocation", {})
                building_location_id = location_data.get("building_location_id")
                if building_location_id:
                    location = db.query(BuildingLocationModel).filter_by(id=building_location_id).first()
                    if location:
                        location.address_municipality = location_data.get("address_municipality", location.address_municipality)
                        location.address_barangay = location_data.get("address_barangay", location.address_barangay)
                        location.street = location_data.get("street", location.street)
                        location.address_province = location_data.get("address_province", location.address_province)
                        location.bcode = location_data.get("bcode", location.bcode)
                        location.mun_code = location_data.get("mun_code", location.mun_code)
                        location.image_list = json.dumps(upload_images_and_get_urls(location_data.get("image_list", []), owner.owner))
                        db.flush()
                        updated_ids["building_location_id"] = location.id

                # 6. Update General Description
                gen_desc_data = request.get("generalDescription", {})
                general_description_id = gen_desc_data.get("general_description_id")
                if general_description_id:
                    gen_desc = db.query(GeneralDescriptionModel).filter_by(id=general_description_id).first()
                    if gen_desc:
                        gen_desc.building_permit_no = gen_desc_data.get("building_permit_no", gen_desc.building_permit_no)
                        gen_desc.certificate_of_completion_issued_on = gen_desc_data.get("certificate_of_completion_issued_on", gen_desc.certificate_of_completion_issued_on)
                        gen_desc.certificate_of_occupancy_issued_on = gen_desc_data.get("certificate_of_occupancy_issued_on", gen_desc.certificate_of_occupancy_issued_on)
                        gen_desc.date_of_occupied = gen_desc_data.get("date_of_occupied", gen_desc.date_of_occupied)
                        gen_desc.bldg_age = gen_desc_data.get("bldg_age", gen_desc.bldg_age)
                        gen_desc.no_of_storeys = gen_desc_data.get("no_of_storeys", gen_desc.no_of_storeys)
                        gen_desc.area_of_1st_floor = gen_desc_data.get("area_of_1st_floor", gen_desc.area_of_1st_floor)
                        gen_desc.area_of_2nd_floor = gen_desc_data.get("area_of_2nd_floor", gen_desc.area_of_2nd_floor)
                        gen_desc.area_of_3rd_floor = gen_desc_data.get("area_of_3rd_floor", gen_desc.area_of_3rd_floor)
                        gen_desc.area_of_4th_floor = gen_desc_data.get("area_of_4th_floor", gen_desc.area_of_4th_floor)
                        gen_desc.total_floor_area = gen_desc_data.get("total_floor_area", gen_desc.total_floor_area)
                        gen_desc.kind_of_bldg = gen_desc_data.get("kind_of_bldg", gen_desc.kind_of_bldg)
                        gen_desc.structural_type = gen_desc_data.get("structural_type", gen_desc.structural_type)
                        gen_desc.unit_value = gen_desc_data.get("unitValue", gen_desc.unit_value)
                        gen_desc.cct_image = json.dumps(upload_images_and_get_urls(gen_desc_data.get("cct_image", []), owner.owner))
                        gen_desc.floor_plan_image = json.dumps(upload_images_and_get_urls(gen_desc_data.get("floor_plan_image", []), owner.owner))
                        db.flush()
                        updated_ids["general_description_id"] = gen_desc.id

                # 7. Update Property Appraisal
                appraisal_data = request.get("propertyAppraisal", {})
                property_appraisal_id = appraisal_data.get("property_appraisal_id")
                if property_appraisal_id:
                    appraisal = db.query(PropertyAppraisalModel).filter_by(id=property_appraisal_id).first()
                    if appraisal:
                        appraisal.building_type = appraisal_data.get("buildingType", appraisal.building_type)
                        appraisal.building_structure = appraisal_data.get("buildingStructure", appraisal.building_structure)
                        appraisal.total_area = appraisal_data.get("totalArea", appraisal.total_area)
                        appraisal.unit_value = appraisal_data.get("unitValue", appraisal.unit_value)
                        appraisal.smv = appraisal_data.get("smv", appraisal.smv)
                        appraisal.base_market_value = appraisal_data.get("baseMarketValue", appraisal.base_market_value)
                        appraisal.depreciation = appraisal_data.get("depreciation", appraisal.depreciation)
                        appraisal.market_value = appraisal_data.get("marketValue", appraisal.market_value)
                        db.flush()
                        updated_ids["property_appraisal_id"] = appraisal.id

                # 8. Update Structural Material
                struct_material_data = request.get("structuralMaterial", {})
                structural_material_id = struct_material_data.get("structural_material_id")
                if structural_material_id:
                    struct_material = db.query(StructuralMaterialModel).filter_by(id=structural_material_id).first()
                    if struct_material:
                        struct_material.material_data = struct_material_data.get("material_data", struct_material.material_data)
                        struct_material.truss_other = struct_material_data.get("truss_other", struct_material.truss_other)
                        db.flush()
                        updated_ids["structural_material_id"] = struct_material.id

                # 9. Update Additional Items (list)
                additional_items_data = request.get("additionalItems", {}).get("items", [])
                existing_additional_items = {item.id: item for item in assessment.additional_items}
                sent_ids = set()
                for item in additional_items_data:
                    item_id = item.get("id")
                    if item_id and item_id in existing_additional_items:
                        add_item = existing_additional_items[item_id]
                        add_item.label = item.get("label", add_item.label)
                        add_item.item_value = item.get("value", add_item.item_value)
                        add_item.quantity = item.get("quantity", add_item.quantity)
                        add_item.amount = item.get("amount", add_item.amount)
                        add_item.description = item.get("description", add_item.description)
                        db.flush()
                        sent_ids.add(item_id)
                    else:
                        # New item
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
                        sent_ids.add(add_item.id)
                # Delete items not in request
                for item_id, item in existing_additional_items.items():
                    if item_id not in sent_ids:
                        db.delete(item)
                updated_ids["additional_item_ids"] = list(sent_ids)

                # 10. Update Additional Items Summary
                add_summary_data = request.get("additionalItems", {})
                additional_items_summary_id = add_summary_data.get("additional_items_summary_id")
                if additional_items_summary_id:
                    add_summary = db.query(AdditionalItemsSummaryModel).filter_by(id=additional_items_summary_id).first()
                    if add_summary:
                        add_summary.total = add_summary_data.get("total", add_summary.total)
                        add_summary.sub_total = add_summary_data.get("subTotal", add_summary.sub_total)
                        db.flush()
                        updated_ids["additional_items_summary_id"] = add_summary.id

                # 11. Update Property Assessment Items (list)
                property_assessment_items_data = request.get("propertyAssessment", {}).get("items", [])
                existing_assessment_items = {item.id: item for item in assessment.assessment_items}
                sent_assess_ids = set()
                for item in property_assessment_items_data:
                    item_id = item.get("id")
                    if item_id and item_id in existing_assessment_items:
                        assess_item = existing_assessment_items[item_id]
                        assess_item.area = item.get("area", assess_item.area)
                        assess_item.unit_value = item.get("unitValue", assess_item.unit_value)
                        assess_item.smv = item.get("smv", assess_item.smv)
                        assess_item.base_market_value = item.get("baseMarketValue", assess_item.base_market_value)
                        assess_item.depreciation_percentage = item.get("depreciationPercentage", assess_item.depreciation_percentage)
                        assess_item.depreciator_cost = item.get("depreciatorCost", assess_item.depreciator_cost)
                        assess_item.market_value = item.get("marketValue", assess_item.market_value)
                        assess_item.building_category = item.get("buildingCategory", assess_item.building_category)
                        db.flush()
                        sent_assess_ids.add(item_id)
                    else:
                        # New item
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
                        sent_assess_ids.add(assess_item.id)
                # Delete items not in request
                for item_id, item in existing_assessment_items.items():
                    if item_id not in sent_assess_ids:
                        db.delete(item)
                updated_ids["property_assessment_item_ids"] = list(sent_assess_ids)

                # 12. Update Memoranda (list)
                memoranda_data = request.get("memoranda", [])
                existing_memos = {memo.id: memo for memo in assessment.memoranda}
                sent_memo_ids = set()
                for memo in memoranda_data:
                    memo_id = memo.get("id")
                    if memo_id and memo_id in existing_memos:
                        memorandum = existing_memos[memo_id]
                        memorandum.date = memo.get("date", memorandum.date)
                        memorandum.details = memo.get("details", memorandum.details)
                        db.flush()
                        sent_memo_ids.add(memo_id)
                    else:
                        # New memo
                        memorandum = MemorandumModel(
                            assessment_id=assessment.id,
                            date=memo.get("date"),
                            details=memo.get("details", "")
                        )
                        db.add(memorandum)
                        db.flush()
                        sent_memo_ids.add(memorandum.id)
                # Delete memos not in request
                for memo_id, memo in existing_memos.items():
                    if memo_id not in sent_memo_ids:
                        db.delete(memo)
                updated_ids["memorandum_ids"] = list(sent_memo_ids)

                # 13. Update Superseded Records (list)
                superseded_data = request.get("recordOfSupersededAssessment", {}).get("records", [])
                existing_superseded = {rec.id: rec for rec in assessment.superseded_records}
                sent_superseded_ids = set()
                for record in superseded_data:
                    record_id = record.get("id")
                    if record_id and record_id in existing_superseded:
                        superseded = existing_superseded[record_id]
                        superseded.pin = record.get("pin", superseded.pin)
                        superseded.td_arp_no = record.get("tdArpNo", superseded.td_arp_no)
                        superseded.total_assessed_value = record.get("totalAssessedValue", superseded.total_assessed_value)
                        superseded.previous_owner = record.get("previousOwner", superseded.previous_owner)
                        superseded.date_of_effectivity = record.get("dateOfEffectivity", superseded.date_of_effectivity)
                        superseded.record_date = record.get("date", superseded.record_date)
                        superseded.assessment = record.get("assessment", superseded.assessment)
                        superseded.tax_mapping = record.get("taxMapping", superseded.tax_mapping)
                        superseded.records = record.get("records", superseded.records)
                        db.flush()
                        sent_superseded_ids.add(record_id)
                    else:
                        # New record
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
                        sent_superseded_ids.add(superseded.id)
                # Delete records not in request
                for record_id, record in existing_superseded.items():
                    if record_id not in sent_superseded_ids:
                        db.delete(record)
                updated_ids["superseded_record_ids"] = list(sent_superseded_ids)

        db.commit()
        return {
            "status": "success",
            "message": "Assessment data updated successfully",
            "data": updated_ids
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail={'message': 'An error occurred while updating the assessment', 'error': str(e)}
        )

