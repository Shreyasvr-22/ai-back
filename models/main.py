"""
FastAPI Backend for Farmer Assistant - Weather Prediction API
Multi-location LSTM Forecasting for Bangalore & surrounding districts
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime
import logging

# Import custom modules
from modules.weather_data import get_weather_data
from modules.multi_location_predictor import MultiLocationPredictor

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Farmer Assistant - Weather Prediction API",
    description="LSTM-based 1-month weather forecasting for multiple districts",
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

# Global state
predictor = None

# ==================== PYDANTIC MODELS ====================

class PredictionResponse(BaseModel):
    date: str
    temp_max: float
    temp_min: float
    rainfall: float

class AlertResponse(BaseModel):
    type: str
    severity: str
    message: str
    date: Optional[str] = None

class WeatherSummary(BaseModel):
    avg_temp_max: float
    avg_temp_min: float
    total_rainfall: float
    max_temp: float
    min_temp: float
    days_with_rain: int

class ForecastRequest(BaseModel):
    latitude: float
    longitude: float
    location: str

class ForecastResponse(BaseModel):
    status: str
    data: Dict
    timestamp: str

# ==================== STARTUP & SHUTDOWN ====================

@app.on_event("startup")
async def startup_event():
    """
    Initialize multi-location predictor on startup
    """
    global predictor
    try:
        logger.info("Initializing Multi-Location Predictor...")
        predictor = MultiLocationPredictor()
        logger.info(f"✓ Predictor initialized successfully")