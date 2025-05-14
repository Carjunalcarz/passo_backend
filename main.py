from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import add_assessment_api, auth, property_assessment_api
from database.database import engine
from models import user_model as models

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
app.include_router(add_assessment_api.router, tags=["add_assessment"])


# python -m uvicorn main:app --reload
