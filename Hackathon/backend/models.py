from sqlalchemy import Column, Integer, Float, String, DateTime
import datetime
import database

class SensorData(database.Base):
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, index=True)
    temperature = Column(Float)
    humidity = Column(Float)
    soil_moisture = Column(Float)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class PredictionLog(database.Base):
    __tablename__ = "prediction_logs"

    id = Column(Integer, primary_key=True, index=True)
    image_path = Column(String)
    prediction = Column(String)
    confidence = Column(Float)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
