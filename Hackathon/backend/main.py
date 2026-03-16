import os
from fastapi import FastAPI, Depends, File, UploadFile, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import africastalking
import warnings

import models
import schemas
import database

# Initialize database
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="AI Crop Disease Early Detection API")

# Setup Africa's Talking
AT_USERNAME = os.getenv("AT_USERNAME", "sandbox")
AT_API_KEY = os.getenv("AT_API_KEY", "")
SMS_RECIPIENT = os.getenv("SMS_RECIPIENT", "+254700000000")

sms = None
if AT_API_KEY:
    try:
        # Ignore warning about africastalking
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            africastalking.initialize(AT_USERNAME, AT_API_KEY)
            sms = africastalking.SMS
            print("Africa's Talking initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize Africa's Talking: {e}")

def send_sms_alert(message: str):
    if sms:
        try:
            response = sms.send(message, [SMS_RECIPIENT])
            print("SMS Sent:", response)
        except Exception as e:
            print("Error sending SMS:", e)
    else:
        print(f"SMS Alert (Mock - No API Key): {message}")

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Backend API is running"}

@app.post("/api/sensors", response_model=schemas.SensorDataResponse)
def add_sensor_data(data: schemas.SensorDataCreate, background_tasks: BackgroundTasks, db: Session = Depends(database.get_db)):
    db_data = models.SensorData(**data.model_dump())
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    
    # Simple Rule-based stress detection
    if data.soil_moisture < 30.0:
        alert_msg = f"Alert (Device {data.device_id}): Soil moisture critically low ({data.soil_moisture}%)."
        background_tasks.add_task(send_sms_alert, alert_msg)
    elif data.temperature > 35.0:
        alert_msg = f"Alert (Device {data.device_id}): High temperature detected ({data.temperature}C)."
        background_tasks.add_task(send_sms_alert, alert_msg)
        
    return db_data

@app.get("/api/sensors", response_model=List[schemas.SensorDataResponse])
def get_sensor_data(limit: int = 100, db: Session = Depends(database.get_db)):
    return db.query(models.SensorData).order_by(models.SensorData.timestamp.desc()).limit(limit).all()

@app.post("/api/predict", response_model=schemas.PredictionResponse)
async def predict_disease(file: UploadFile = File(...), db: Session = Depends(database.get_db)):
    # Actual AI Inference happens here (mocked for context simplicity in this file, actual in ai/)
    prediction_result = "Northern Leaf Blight"
    confidence_score = 0.92
    
    db_pred = models.PredictionLog(
        image_path=file.filename,
        prediction=prediction_result,
        confidence=confidence_score
    )
    db.add(db_pred)
    db.commit()
    db.refresh(db_pred)
    
    return schemas.PredictionResponse(
        id=db_pred.id,
        prediction=prediction_result,
        confidence=confidence_score,
        timestamp=db_pred.timestamp
    )
