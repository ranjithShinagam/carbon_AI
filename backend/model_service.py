import joblib
import os
import pandas as pd

import logging
logger = logging.getLogger(__name__)

# Try to load the model on startup, but allow graceful failure if it doesn't exist yet
# so the backend can run even if it hasn't been trained
class ModelService:
    def __init__(self):
        self.model = None
        self.model_path = os.path.join(os.path.dirname(__file__), "model.pkl")
        self.load_model()
        
    def load_model(self):
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
                logger.info("Model loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
        else:
            logger.warning(f"Model not found at {self.model_path}. Predict will fail until trained.")
            self.model = None

    def predict(self, input_data: dict) -> float:
        if self.model is None:
            # reload just in case it was built post-startup
            self.load_model()
            if self.model is None:
                raise ValueError("Model has not been trained yet. Please run training_pipeline.py")
        
        # XGBoost generally expects a DataFrame matching training features
        # Assuming single row prediction
        features = [
            "Electricity",
            "NRE_consumption",
            "Production",
            "transport_km",
            "raw_material",
            "emp_count"
        ]
        
        # Map our input JSON exactly to the features we trained on
        row = {
            "Electricity": input_data.get("total_energy", 0.0),
            "NRE_consumption": input_data.get("nonrenewable_energy", 0.0),
            "Production": input_data.get("production_output", 0.0),
            "transport_km": input_data.get("transport_distance", 0.0),
            "raw_material": input_data.get("raw_material_usage", 0.0),
            "emp_count": input_data.get("employment_count", 0.0)
        }
        
        df = pd.DataFrame([row], columns=features)
        
        # Convert prediction to python float since it returns numpy float32
        pred = self.model.predict(df)[0]
        return float(pred)

# Singleton instance
model_service = ModelService()
