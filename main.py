"""FastAPI application entry point for the Real Property Tax Assessment System."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import (
    add_assessment_api,
    auth,
    general_revision_api,
    get_assessment_api,
    property_assessment_api,
    unit_cost_api,
)
from database.database import engine
from models import user_model as models
from models import unit_cost_model

# Run migrations
models.Base.metadata.create_all(bind=engine)
unit_cost_model.Base.metadata.create_all(bind=engine)

# Create FastAPI instance
app = FastAPI(
    title="Real Property Tax Assessment System",
    description="API for managing property assessments and owner details",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(property_assessment_api.router)

# app.include_router(
#     property_assessment_api.router,
#     prefix='/municipality',
#     tags=['Municipality'],
# )
app.include_router(
    add_assessment_api.router,
    prefix="/assessment",
    tags=["Assessment"],
)
app.include_router(
    get_assessment_api.router,
    prefix="/assessment",
    tags=["Assessment"],
)
app.include_router(general_revision_api.router)
app.include_router(unit_cost_api.router)
# Note: Start the server with:
# python -m uvicorn main:app --reload
