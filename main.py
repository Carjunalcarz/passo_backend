"""FastAPI application entry point for the Real Property Tax Assessment System."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import add_assessment_api, auth, property_assessment_api
from database.database import engine
from models import user_model as models

# Run migrations
models.Base.metadata.create_all(bind=engine)

# Create FastAPI instance
app = FastAPI(
    title='Real Property Tax Assessment System',
    description='API for managing property assessments and owner details',
    version='1.0.0',
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Include routers
app.include_router(auth.router)
app.include_router(
    add_assessment_api.router,
    prefix='/api/v1',
    tags=['Assessment'],
)

# Note: Start the server with:
# python -m uvicorn main:app --reload
