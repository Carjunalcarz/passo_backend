from datetime import date
from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class ApprovalSection(BaseModel):
    appraised_by: Optional[str] = Field(None, alias="appraisedBy")
    appraised_date: Optional[date] = Field(None, alias="appraisedDate")
    recommending_approval: Optional[str] = Field(None, alias="recommendingApproval")
    municipality_assessor_date: Optional[date] = Field(None, alias="municipalityAssessorDate")
    approved_by_province: Optional[str] = Field(None, alias="approvedByProvince")
    provincial_assessor_date: Optional[date] = Field(None, alias="provincialAssessorDate")

    class Config:
        from_attributes = True
        populate_by_name = True

class OwnerDetails(BaseModel):
    owner: Optional[str] = Field(None)
    owner_address: Optional[str] = Field(None, alias="ownerAddress")
    admin_ben_user: Optional[str] = Field(None, alias="admin_ben_user")
    admin_ben_user_address: Optional[str] = Field(None, alias="adminBenUserAddress")
    transaction_code: Optional[str] = Field(None, alias="transactionCode")
    pin: Optional[str] = Field(None)
    tin: Optional[str] = Field(None)
    tel_no: Optional[str] = Field(None, alias="telNo")
    td: Optional[str] = Field(None)
    image_list: Optional[List[str]] = Field(None, alias="imageList")

    class Config:
        from_attributes = True
        populate_by_name = True

class LandReference(BaseModel):
    land_owner: Optional[str] = Field(None, alias="landOwner")
    block_no: Optional[str] = Field(None, alias="blockNo")
    tdn_no: Optional[str] = Field(None, alias="tdnNo")
    pin: Optional[str] = Field(None)
    lot_no: Optional[str] = Field(None, alias="lotNo")
    survey_no: Optional[str] = Field(None, alias="surveyNo")
    area: Optional[str] = Field(None)

    class Config:
        from_attributes = True
        populate_by_name = True

class BuildingLocation(BaseModel):
    address_municipality: Optional[str] = Field(None, alias="addressMunicipality")
    address_barangay: Optional[str] = Field(None, alias="addressBarangay")
    street: Optional[str] = Field(None, alias="street")
    address_province: Optional[str] = Field(None, alias="addressProvince")
    bcode: Optional[str] = Field(None)
    mun_code: Optional[str] = Field(None, alias="munCode")
    image_list: Optional[List[str]] = Field(None, alias="imageList")
    

    class Config:
        from_attributes = True
        populate_by_name = True

class GeneralDescription(BaseModel):
    building_permit_no: Optional[str] = Field(None, alias="buildingPermitNo")
    certificate_of_completion_issued_on: Optional[date] = Field(None, alias="certificateOfCompletionIssuedOn")
    certificate_of_occupancy_issued_on: Optional[date] = Field(None, alias="certificateOfOccupancyIssuedOn")
    date_of_occupied: Optional[date] = Field(None, alias="dateOfOccupied")
    bldg_age: Optional[str] = Field(None, alias="bldgAge")
    no_of_storeys: Optional[str] = Field(None, alias="noOfStoreys")
    area_of_1st_floor: Optional[str] = Field(None, alias="areaOf1stFloor")
    area_of_2nd_floor: Optional[str] = Field(None, alias="areaOf2ndFloor")
    area_of_3rd_floor: Optional[str] = Field(None, alias="areaOf3rdFloor")
    area_of_4th_floor: Optional[str] = Field(None, alias="areaOf4thFloor")
    total_floor_area: Optional[float] = Field(None, alias="totalFloorArea")
    kind_of_bldg: Optional[str] = Field(None, alias="kindOfBldg")
    structural_type: Optional[str] = Field(None, alias="structuralType")
    unit_value: Optional[float] = Field(None, alias="unitValue")

    class Config:
        from_attributes = True
        populate_by_name = True

class PropertyAppraisal(BaseModel):
    building_type: Optional[str] = Field(None, alias="buildingType")
    building_structure: Optional[str] = Field(None, alias="buildingStructure")
    total_area: Optional[float] = Field(None, alias="totalArea")
    unit_value: Optional[float] = Field(None, alias="unitValue")
    smv: Optional[float] = Field(None)
    base_market_value: Optional[float] = Field(None, alias="baseMarketValue")
    depreciation: Optional[float] = Field(None)
    market_value: Optional[float] = Field(None, alias="marketValue")

    class Config:
        from_attributes = True
        populate_by_name = True

class AdditionalItemValue(BaseModel):
    label: str
    rate_per_sq_m: Optional[float] = Field(None, alias="ratePerSqM")
    percentage: Optional[float] = None

    class Config:
        populate_by_name = True

class AdditionalItemEntry(BaseModel):
    id: int
    label: str
    value: AdditionalItemValue
    quantity: float
    amount: float
    description: Optional[str] = None

class AdditionalItems(BaseModel):
    items: List[AdditionalItemEntry]
    total: float
    sub_total: float = Field(alias="subTotal")

    class Config:
        from_attributes = True
        populate_by_name = True

class EffectivityOfAssessment(BaseModel):
    quarter: Optional[str] = Field(None)

class AssessmentItem(BaseModel):
    id: str
    area: float = Field(0)
    unit_value: float = Field(0, alias="unitValue")
    smv: float = Field(0)
    base_market_value: float = Field(0, alias="baseMarketValue")
    depreciation_percentage: float = Field(0, alias="depreciationPercentage")
    depreciator_cost: float = Field(0, alias="depreciatorCost")
    market_value: float = Field(0, alias="marketValue")
    building_category: str = Field("", alias="buildingCategory")

    class Config:
        populate_by_name = True

class PropertyAssessment(BaseModel):
    id: int
    assessment_id: int = Field(alias="assessmentId")
    assessment_level: str = Field(alias="assessmentLevel")
    assessment_level_value: float = Field(alias="assessmentLevel")
    assessment_value: float = Field(alias="assessmentValue")
    total_area: float = Field(alias="totalArea")
    market_value: float = Field(alias="marketValue")
    building_category: str = Field(alias="buildingCategory")
    eff_year: str = Field(alias="effYear")
    eff_quarter: str = Field(alias="effQuarter")
    taxable : int = Field(alias="taxable")
    items: List[AssessmentItem]

    class Config:
        from_attributes = True
        populate_by_name = True

class Memorandum(BaseModel):
    date: date
    details: str

class SupersededRecord(BaseModel):
    id: int
    pin: str
    td_arp_no: str = Field(alias="tdArpNo")
    total_assessed_value: str = Field(alias="totalAssessedValue")
    previous_owner: str = Field(alias="previousOwner")
    date_of_effectivity: date = Field(alias="dateOfEffectivity")
    record_date: date = Field(alias="date")
    assessment: str
    tax_mapping: str = Field(alias="taxMapping")
    records: str

    class Config:
        populate_by_name = True

class RecordOfSupersededAssessment(BaseModel):
    records: List[SupersededRecord]

    class Config:
        from_attributes = True

class CompleteAssessmentRequest(BaseModel):
    approval_section: ApprovalSection = Field(alias="approvalSection")
    street: Optional[str] = Field(None)
    owner_details: OwnerDetails = Field(alias="ownerDetails")
    land_reference: LandReference = Field(alias="landReference")
    building_location: BuildingLocation = Field(alias="buildingLocation")
    address_municipality: str = Field(alias="addressMunicipality")
    address_barangay: str = Field(alias="addressBarangay")
    address_province: str = Field(alias="addressProvince")
    general_description: GeneralDescription = Field(alias="generalDescription")
    cct: Dict = Field(default_factory=dict)
    floor_plan: List[Dict] = Field(default_factory=list, alias="floorPlan")
    structural_material: Dict = Field(default_factory=dict, alias="structuralMaterial")
    truss_other: Optional[str] = Field(None, alias="trussOther")
    property_appraisal: PropertyAppraisal = Field(alias="propertyAppraisal")
    additional_item: Optional[str] = Field(None, alias="additionalItem")
    additional_items: AdditionalItems = Field(alias="additionalItems")
    property_assessment: PropertyAssessment = Field(alias="propertyAssessment")
    assessment_value: float = Field(alias="assessmentValue")
    building_category: str = Field(alias="buildingCategory")
    taxable_value: List[str] = Field(alias="taxableValue")
    effectivity_of_assessment: str = Field(alias="effectivityOfAssessment")
    assessment_level: float = Field(alias="assessmentLevel")
    memoranda: List[Memorandum]
    record_of_superseded_assessment: RecordOfSupersededAssessment = Field(alias="recordOfSupersededAssessment")

    class Config:
        from_attributes = True
        populate_by_name = True