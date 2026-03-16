from pydantic import BaseModel
from datetime import datetime

class SensorDataCreate(BaseModel):
    device_id: str
    temperature: float
    humidity: float
    soil_moisture: float

class SensorDataResponse(SensorDataCreate):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class PredictionResponse(BaseModel):
    id: int
    prediction: str
    confidence: float
    timestamp: datetime
