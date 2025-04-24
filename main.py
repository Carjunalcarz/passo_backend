from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import user_model as models
from database.database import engine
from api import auth, property_assessment_api

# Run migrations
models.Base.metadata.create_all(bind=engine)

# Create FastAPI instance
app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or use a specific list: ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(property_assessment_api.router)


# python -m uvicorn main:app --reload