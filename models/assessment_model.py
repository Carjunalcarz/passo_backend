from sqlalchemy import Column, Integer, String, Float, Boolean, Date, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from database.database import engine

Base = declarative_base()

class OwnerDetailsModel(Base):
    __tablename__ = "owner_details"
    __table_args__ = {'schema': 'Assessor2025'}
    
    id = Column(Integer, primary_key=True, index=True)
    owner = Column(String)
    owner_address = Column(String)
    admin_ben_user = Column(String)
    transaction_code = Column(String)
    pin = Column(String)
    tin = Column(String)
    tel_no = Column(String)
    td = Column(String)
    
    # Relationships
    approval = relationship("ApprovalSectionModel", back_populates="owner", uselist=False)
    land_reference = relationship("LandReferenceModel", back_populates="owner", uselist=False)
    building_assessment = relationship("BuildingAssessmentModel", back_populates="owner", uselist=False)

class ApprovalSectionModel(Base):
    __tablename__ = "approval_section"
    __table_args__ = {'schema': 'Assessor2025'}
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("Assessor2025.owner_details.id"))
    tdn = Column(String)
    appraised_by = Column(String)
    appraised_date = Column(Date)
    recommending_approval = Column(String)
    municipality_assessor_date = Column(Date)
    approved_by_province = Column(String)
    provincial_assessor_date = Column(Date)
    
    # Relationships
    owner = relationship("OwnerDetailsModel", back_populates="approval")

class LandReferenceModel(Base):
    __tablename__ = "land_reference"
    __table_args__ = {'schema': 'Assessor2025'}
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("Assessor2025.owner_details.id"))
    land_owner = Column(String)
    block_no = Column(String)
    tdn_no = Column(String)
    pin = Column(String)
    lot_no = Column(String)
    survey_no = Column(String)
    area = Column(String)
    
    # Relationships
    owner = relationship("OwnerDetailsModel", back_populates="land_reference")

class BuildingLocationModel(Base):
    __tablename__ = "building_location"
    __table_args__ = {'schema': 'Assessor2025'}

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("Assessor2025.building_assessment.id"))
    address_municipality = Column(String)
    address_barangay = Column(String)
    street = Column(String)
    address_province = Column(String)
    
    # Relationships
    assessment = relationship("BuildingAssessmentModel", back_populates="location")

class GeneralDescriptionModel(Base):
    __tablename__ = "general_description"
    __table_args__ = {'schema': 'Assessor2025'}
    
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("Assessor2025.building_assessment.id"))
    building_permit_no = Column(String)
    certificate_of_completion_issued_on = Column(Date)
    certificate_of_occupancy_issued_on = Column(Date)
    date_of_occupied = Column(Date)
    bldg_age = Column(String)
    no_of_storeys = Column(String)
    area_of_1st_floor = Column(String)
    area_of_2nd_floor = Column(String)
    area_of_3rd_floor = Column(String)
    area_of_4th_floor = Column(String)
    total_floor_area = Column(Float)
    kind_of_bldg = Column(String)
    structural_type = Column(String)
    unit_value = Column(Float)
    
    # Relationships
    assessment = relationship("BuildingAssessmentModel", back_populates="general_description")

class PropertyAppraisalModel(Base):
    __tablename__ = "property_appraisal"
    __table_args__ = {'schema': 'Assessor2025'}
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("Assessor2025.building_assessment.id"))
    building_type = Column(String)
    building_structure = Column(String)
    total_area = Column(Float)
    unit_value = Column(Float)
    smv = Column(Float)
    base_market_value = Column(Float)
    depreciation = Column(Float)
    market_value = Column(Float)
    
    # Relationships
    assessment = relationship("BuildingAssessmentModel", back_populates="property_appraisal")

class AdditionalItemModel(Base):
    __tablename__ = "additional_items"
    __table_args__ = {'schema': 'Assessor2025'}
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("Assessor2025.building_assessment.id"))
    item_id = Column(Integer)
    label = Column(String)
    item_value = Column(JSON)  # Store the value object as JSON
    quantity = Column(Float)
    amount = Column(Float)
    description = Column(String)
    
    # Relationships
    assessment = relationship("BuildingAssessmentModel", back_populates="additional_items")

class AdditionalItemsSummaryModel(Base):
    __tablename__ = "additional_items_summary"
    __table_args__ = {'schema': 'Assessor2025'}
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("Assessor2025.building_assessment.id"))
    total = Column(Float)
    sub_total = Column(Float)
    
    # Relationships
    assessment = relationship("BuildingAssessmentModel", back_populates="additional_items_summary")

class PropertyAssessmentItemModel(Base):
    __tablename__ = "property_assessment_items"
    __table_args__ = {'schema': 'Assessor2025'}
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("Assessor2025.building_assessment.id"))
    item_id = Column(String)
    area = Column(Float)
    unit_value = Column(Float)
    smv = Column(Float)
    base_market_value = Column(Float)
    depreciation_percentage = Column(Float)
    depreciator_cost = Column(Float)
    market_value = Column(Float)
    building_category = Column(String)
    
    # Relationships
    assessment = relationship("BuildingAssessmentModel", back_populates="assessment_items")

class MemorandumModel(Base):
    __tablename__ = "memoranda"
    __table_args__ = {'schema': 'Assessor2025'}
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("Assessor2025.building_assessment.id"))
    date = Column(Date)
    details = Column(String)
    
    # Relationships
    assessment = relationship("BuildingAssessmentModel", back_populates="memoranda")

class SupersededRecordModel(Base):
    __tablename__ = "superseded_records"
    __table_args__ = {'schema': 'Assessor2025'}
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("Assessor2025.building_assessment.id"))
    pin = Column(String)
    td_arp_no = Column(String)
    total_assessed_value = Column(String)
    previous_owner = Column(String)
    date_of_effectivity = Column(Date)
    record_date = Column(Date)
    assessment = Column(String)
    tax_mapping = Column(String)
    records = Column(String)
    
    # Relationships
    building_assessment = relationship("BuildingAssessmentModel", back_populates="superseded_records")

class StructuralMaterialModel(Base):
    __tablename__ = "structural_materials"
    __table_args__ = {'schema': 'Assessor2025'}
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("Assessor2025.building_assessment.id"))
    material_data = Column(JSON)  # Store all the boolean fields as JSON
    truss_other = Column(String)
    
    # Relationships
    assessment = relationship("BuildingAssessmentModel", back_populates="structural_material")

class BuildingAssessmentModel(Base):
    __tablename__ = "building_assessment"
    __table_args__ = {'schema': 'Assessor2025'}
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("Assessor2025.owner_details.id"))
    street = Column(String)
    address_municipality = Column(String)
    address_province = Column(String)
    address_barangay = Column(String)
    assessment_value = Column(Float)
    building_category = Column(String)
    taxable_value = Column(JSON)  # Store the list as JSON
    effectivity_of_assessment = Column(String)
    assessment_level = Column(Float)
    cct = Column(JSON)
    floor_plan = Column(JSON)
    additional_item = Column(String)
    
    # Relationships
    owner = relationship("OwnerDetailsModel", back_populates="building_assessment")
    location = relationship("BuildingLocationModel", back_populates="assessment", uselist=False)
    general_description = relationship("GeneralDescriptionModel", back_populates="assessment", uselist=False)
    property_appraisal = relationship("PropertyAppraisalModel", back_populates="assessment", uselist=False)
    additional_items = relationship("AdditionalItemModel", back_populates="assessment")
    additional_items_summary = relationship("AdditionalItemsSummaryModel", back_populates="assessment", uselist=False)
    assessment_items = relationship("PropertyAssessmentItemModel", back_populates="assessment")
    memoranda = relationship("MemorandumModel", back_populates="assessment")
    superseded_records = relationship("SupersededRecordModel", back_populates="building_assessment")
    structural_material = relationship("StructuralMaterialModel", back_populates="assessment", uselist=False)

# Create all tables defined in your models
Base.metadata.create_all(bind=engine)