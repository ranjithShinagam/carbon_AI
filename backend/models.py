from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    predictions = relationship(
        "PredictionHistory",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    chat_messages = relationship(
        "ChatMessage",
        back_populates="user",
        cascade="all, delete-orphan"
    )


class PredictionHistory(Base):
    __tablename__ = "prediction_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # ============================================================
    # INPUTS
    # ============================================================

    total_energy = Column(Float, nullable=False)
    renewable_energy = Column(Float, nullable=False)
    nonrenewable_energy = Column(Float, nullable=False)
    production_output = Column(Float, nullable=False)
    transport_distance = Column(Float, nullable=False)
    raw_material_usage = Column(Float, nullable=False)
    employment_count = Column(Float, nullable=False)
    
    sector = Column(String, nullable=True)
    industry_sector = Column(String, nullable=True)
    transport_mode = Column(String, nullable=True)

    # ============================================================
    # DERIVED / OUTPUT VALUES
    # ============================================================

    predicted_co2_emission = Column(Float, nullable=False)
    carbon_intensity = Column(Float, nullable=False)
    energy_per_employee = Column(Float, nullable=False)
    renewable_energy_ratio = Column(Float, nullable=False)
    nonrenewable_energy_ratio = Column(Float, nullable=False)

    # ============================================================
    # METADATA
    # ============================================================

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    user = relationship(
        "User",
        back_populates="predictions"
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    session_id = Column(String(128), index=True, nullable=False)
    role = Column(String(20), nullable=False)  # "user" or "model"
    content = Column(Text, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    user = relationship(
        "User",
        back_populates="chat_messages"
    )