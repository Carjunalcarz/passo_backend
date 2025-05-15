from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from datetime import date
from .approval_section_schema import ApprovalSection
from .owner_details_schema import OwnerDetails
from .land_reference_schema import LandReference
from .building_location_schema import BuildingLocation
from .general_description_schema import GeneralDescription
from .structural_material_schema import StructuralMaterial
from .property_appraisal_schema import PropertyAppraisal
from .additional_items_schema import AdditionalItems
from .property_assessment_schema import PropertyAssessment
from .memoranda_schema import Memorandum
from .record_superseded_assessment_schema import RecordOfSupersededAssessment

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