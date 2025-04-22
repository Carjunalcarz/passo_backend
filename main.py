from fastapi import FastAPI
from models import user_model as models
from database.database import engine
from api import auth

# Run migrations
models.Base.metadata.create_all(bind=engine)

# Create FastAPI instance
app = FastAPI()

# Include routers
app.include_router(auth.router)


# python -m uvicorn main:app --reload