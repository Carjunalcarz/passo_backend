from datetime import date
from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class ApprovalSection(BaseModel):
    appraisedBy: Optional[str] = Field(None)
    appraisedDate: Optional[date] = Field(None)
    recommendingApproval: Optional[str] = Field(None)
    municipalityAssessorDate: Optional[date] = Field(None)
    approvedByProvince: Optional[str] = Field(None)
    provincialAssessorDate: Optional[date] = Field(None)

    class Config:
        from_attributes = True

class OwnerDetails(BaseModel):
    owner: Optional[str] = Field(None)
    ownerAddress: Optional[str] = Field(None)
    admin_ben_user: Optional[str] = Field(None)
    transactionCode: Optional[str] = Field(None)
    pin: Optional[str] = Field(None)
    tin: Optional[str] = Field(None)
    telNo: Optional[str] = Field(None)
    td: Optional[str] = Field(None)

    class Config:
        from_attributes = True

class LandReference(BaseModel):
    land_owner: Optional[str] = Field(None)
    block_no: Optional[str] = Field(None)
    tdn_no: Optional[str] = Field(None)
    pin: Optional[str] = Field(None)
    lot_no: Optional[str] = Field(None)
    survey_no: Optional[str] = Field(None)
    area: Optional[str] = Field(None)

    class Config:
        from_attributes = True

class BuildingLocation(BaseModel):
    address_municipality: Optional[str] = Field(None)
    address_barangay: Optional[str] = Field(None)
    street: Optional[str] = Field(None)
    address_province: Optional[str] = Field(None)

    class Config:
        from_attributes = True

class GeneralDescription(BaseModel):
    building_permit_no: Optional[str] = Field(None)
    certificate_of_completion_issued_on: Optional[date] = Field(None)
    certificate_of_occupancy_issued_on: Optional[date] = Field(None)
    date_of_occupied: Optional[date] = Field(None)
    bldg_age: Optional[str] = Field(None)
    no_of_storeys: Optional[str] = Field(None)
    area_of_1st_floor: Optional[str] = Field(None)
    area_of_2nd_floor: Optional[str] = Field(None)
    area_of_3rd_floor: Optional[str] = Field(None)
    area_of_4th_floor: Optional[str] = Field(None)
    total_floor_area: Optional[float] = Field(None)
    kind_of_bldg: Optional[str] = Field(None)
    structural_type: Optional[str] = Field(None)
    unitValue: Optional[float] = Field(None)

    class Config:
        from_attributes = True

class PropertyAppraisal(BaseModel):
    buildingType: Optional[str] = Field(None)
    buildingStructure: Optional[str] = Field(None)
    totalArea: Optional[float] = Field(None)
    unitValue: Optional[float] = Field(None)
    smv: Optional[float] = Field(None)
    baseMarketValue: Optional[float] = Field(None)
    depreciation: Optional[float] = Field(None)
    marketValue: Optional[float] = Field(None)

    class Config:
        from_attributes = True

class AdditionalItemValue(BaseModel):
    label: str
    ratePerSqM: Optional[float] = None
    percentage: Optional[float] = None

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
    subTotal: float

    class Config:
        from_attributes = True

class EffectivityOfAssessment(BaseModel):
    quarter: Optional[str] = Field(None)

class AssessmentItem(BaseModel):
    id: str
    area: float = Field(0)
    unitValue: float = Field(0)
    smv: float = Field(0)
    baseMarketValue: float = Field(0)
    depreciationPercentage: float = Field(0)
    depreciatorCost: float = Field(0)
    marketValue: float = Field(0)
    buildingCategory: str = Field("")

class PropertyAssessment(BaseModel):
    assessmentLevel: float
    assessmentValue: float
    totalArea: float
    marketValue: float
    buildingCategory: str
    effectivityOfAssessment: EffectivityOfAssessment
    items: List[AssessmentItem]

    class Config:
        from_attributes = True

class Memorandum(BaseModel):
    date: date
    details: str

class SupersededRecord(BaseModel):
    pin: str
    tdArpNo: str
    totalAssessedValue: str
    previousOwner: str
    dateOfEffectivity: date
    date: date
    assessment: str
    taxMapping: str
    records: str

class RecordOfSupersededAssessment(BaseModel):
    records: List[SupersededRecord]

    class Config:
        from_attributes = True

class CompleteAssessmentRequest(BaseModel):
    approvalSection: ApprovalSection
    street: Optional[str] = Field(None)
    ownerDetails: OwnerDetails
    landReference: LandReference
    buildingLocation: BuildingLocation
    address_municipality: str
    address_barangay: str
    address_province: str
    generalDescription: GeneralDescription
    cct: Dict = Field(default_factory=dict)
    floor_plan: List[Dict] = Field(default_factory=list)
    structuralMaterial: Dict = Field(default_factory=dict)
    truss_other: Optional[str] = Field(None)
    propertyAppraisal: PropertyAppraisal
    additionalItem: Optional[str] = Field(None)
    additionalItems: AdditionalItems
    propertyAssessment: PropertyAssessment
    assessmentValue: float
    buildingCategory: str
    taxableValue: List[str]
    effectivityOfAssessment: str
    assessmentLevel: float
    memoranda: List[Memorandum]
    recordOfSupersededAssessment: RecordOfSupersededAssessment

    class Config:
        from_attributes = True