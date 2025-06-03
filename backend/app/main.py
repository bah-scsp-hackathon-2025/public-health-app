from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.routers import users, alerts, dashboard
from app.database import engine, Base
from app.config import settings

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="BAH Public Health App",
    description="An app to help policy makers make informed decisions",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router)
app.include_router(alerts.router)
app.include_router(dashboard.router)


@app.get("/")
async def root():
    return {"message": "BAH Public Health App"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
