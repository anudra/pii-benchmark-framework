# FastAPI application entry point
# This file initializes the FastAPI app and includes all routes

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os

from .database.db import init_db
from .api.routes import router

# Initialize FastAPI app
app = FastAPI(
    title="PII Evaluation & Benchmarking Framework",
    description="Evaluate PII detection and redaction system performance",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)

# Redirect root to dashboard
@app.get("/")
async def root():
    """Redirect to dashboard"""
    return RedirectResponse(url="/dashboard.html")

# Serve frontend static files
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    print("Database initialized")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "PII Evaluation Framework is running"}
