from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
import uvicorn
import pandas as pd

import database, models
from routers import auth
from model_service import model_service
from feature_engineering import calculate_post_prediction_features

# Create DB Tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="AI Carbon Intelligence API")

# Setup CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(auth.router)

from model_service import model_service
from feature_engineering import calculate_post_prediction_features



class PredictionRequest(BaseModel):
    total_energy: float
    nonrenewable_energy: float
    production_output: float
    transport_distance: float
    raw_material_usage: float
    employment_count: float

@app.post("/predict")
def predict_emissions(
    request: PredictionRequest, 
    db: Session = Depends(database.get_db),
    user: models.User | None = Depends(auth.get_current_user_optional)
):
    input_data = request.model_dump()
    try:
        predicted_co2 = model_service.predict(input_data)
        
        # Calculate derived features
        derived = calculate_post_prediction_features(
            predicted_co2=predicted_co2,
            production_output=request.production_output,
            total_energy=request.total_energy,
            employment_count=request.employment_count
        )
        
        
        # Save to DB if user is authenticated
        if user:
            history = models.PredictionHistory(
                user_id=user.id,
                total_energy=request.total_energy,
                nonrenewable_energy=request.nonrenewable_energy,
                production_output=request.production_output,
                transport_distance=request.transport_distance,
                raw_material_usage=request.raw_material_usage,
                employment_count=request.employment_count,
                predicted_co2_emission=predicted_co2,
                carbon_intensity=derived["carbon_intensity"],
                energy_per_employee=derived["energy_per_employee"]
            )
            db.add(history)
            db.commit()
            
        return {
            "predicted_co2_emission": predicted_co2,
            "carbon_intensity": derived["carbon_intensity"],
            "energy_per_employee": derived["energy_per_employee"]
        }
    except ValueError as ve:
        raise HTTPException(status_code=500, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred during prediction.")

@app.get("/history")
def get_prediction_history(
    db: Session = Depends(database.get_db), 
    user: models.User = Depends(auth.get_current_user)
):
    histories = db.query(models.PredictionHistory).filter(models.PredictionHistory.user_id == user.id).order_by(models.PredictionHistory.created_at.desc()).all()
    return histories

@app.get("/dataset-insights")
def get_dataset_insights():
    try:
        df = pd.read_csv("trail_df.csv")
        corrs = df.corr()["target"].drop("target")
        
        stats = {
            "total_records": int(len(df)),
            "averages": {k: float(v) for k, v in df.mean().items()},
            "min": {k: float(v) for k, v in df.min().items()},
            "max": {k: float(v) for k, v in df.max().items()},
            "correlations": {k: float(v) for k, v in corrs.items()}
        }
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze dataset: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
