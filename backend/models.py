from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    predictions = relationship("PredictionHistory", back_populates="user")


class PredictionHistory(Base):
    __tablename__ = "prediction_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Inputs
    total_energy = Column(Float)
    nonrenewable_energy = Column(Float)
    production_output = Column(Float)
    transport_distance = Column(Float)
    raw_material_usage = Column(Float)
    employment_count = Column(Float)
    
    # Outputs
    predicted_co2_emission = Column(Float)
    carbon_intensity = Column(Float)
    energy_per_employee = Column(Float)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="predictions")
