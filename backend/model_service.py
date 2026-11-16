import os
import json
import logging
from typing import Dict, Any, List, Optional

import joblib
import numpy as np
import pandas as pd

from feature_engineering import calculate_post_prediction_features
from ml.feature_engineering import engineer_features_df
from ml.preprocessing import CarbonDataPreprocessor

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARTIFACTS_DIR = os.path.join(BASE_DIR, "ml", "artifacts")

MODEL_PATH = os.path.join(ARTIFACTS_DIR, "model.pkl")
FALLBACK_MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")
PREPROCESSOR_PATH = os.path.join(ARTIFACTS_DIR, "preprocessor.pkl")
FEATURE_METADATA_PATH = os.path.join(ARTIFACTS_DIR, "feature_metadata.json")
MODEL_METADATA_PATH = os.path.join(ARTIFACTS_DIR, "model_metadata.json")
FALLBACK_METADATA_PATH = os.path.join(BASE_DIR, "model_metadata.json")
FEATURE_IMPORTANCE_PATH = os.path.join(BASE_DIR, "feature_importance.csv")

RAW_NUMERIC_COLUMNS = [
    "Total_Energy_Consumption_kWh",
    "Renewable_Energy_Consumption_kWh",
    "NonRenewable_Energy_Consumption_kWh",
    "Production_Output_Units",
    "Supply_Chain_Transport_km",
    "Raw_Material_Usage_kg",
    "Employment_Count",
]


class ModelService:
    def __init__(self):
        self.model = None
        self.preprocessor: Optional[CarbonDataPreprocessor] = None
        self.feature_metadata: Dict[str, Any] = {}
        self.metadata: Dict[str, Any] = {}
        self.final_feature_columns: List[str] = []
        self.categories_map: Dict[str, List[str]] = {}
        self.feature_importance: List[Dict[str, Any]] = []

        self.load_all()

    def load_all(self):
        self.load_feature_metadata()
        self.load_preprocessor()
        self.load_model()
        self.load_metadata()
        self.load_feature_importance()

    def load_feature_metadata(self):
        if os.path.exists(FEATURE_METADATA_PATH):
            try:
                with open(FEATURE_METADATA_PATH, "r", encoding="utf-8") as f:
                    self.feature_metadata = json.load(f)
                self.final_feature_columns = self.feature_metadata.get("final_feature_columns", [])
                self.categories_map = self.feature_metadata.get("categories_map", {})
            except Exception as exc:
                logger.warning(f"Failed to load feature_metadata.json: {exc}")

    def load_preprocessor(self):
        if os.path.exists(PREPROCESSOR_PATH):
            try:
                self.preprocessor = CarbonDataPreprocessor.load(PREPROCESSOR_PATH)
            except Exception as exc:
                logger.warning(f"Failed to load preprocessor.pkl: {exc}")
                self.preprocessor = None

    def load_model(self):
        path = MODEL_PATH if os.path.exists(MODEL_PATH) else FALLBACK_MODEL_PATH
        if not os.path.exists(path):
            logger.warning(f"Model not found at {path}")
            return
        try:
            self.model = joblib.load(path)
            logger.info(f"XGBoost v2 model loaded from {path}")
        except Exception as exc:
            logger.exception(f"Failed to load model: {exc}")
            self.model = None

    def load_metadata(self):
        path = MODEL_METADATA_PATH if os.path.exists(MODEL_METADATA_PATH) else FALLBACK_METADATA_PATH
        if not os.path.exists(path):
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
        except Exception as exc:
            logger.warning(f"Could not load metadata: {exc}")

    def load_feature_importance(self):
        if self.model is not None and hasattr(self.model, "feature_importances_") and self.final_feature_columns:
            try:
                importances = self.model.feature_importances_
                pairs = sorted(
                    zip(self.final_feature_columns, importances),
                    key=lambda x: float(x[1]),
                    reverse=True,
                )
                self.feature_importance = [
                    {"feature": name, "importance": float(val)}
                    for name, val in pairs
                ]
                return
            except Exception as exc:
                logger.warning(f"Could not compute model feature importance: {exc}")

        if os.path.exists(FEATURE_IMPORTANCE_PATH):
            try:
                df = pd.read_csv(FEATURE_IMPORTANCE_PATH)
                self.feature_importance = df.to_dict(orient="records")
            except Exception as exc:
                logger.warning(f"Could not load feature_importance.csv: {exc}")

    def _ensure_model_loaded(self):
        if self.model is None or self.preprocessor is None or not self.final_feature_columns:
            self.load_all()
        if self.model is None:
            raise RuntimeError("XGBoost model is not available. Run `python -m ml.train` first.")
        if self.preprocessor is None or not self.final_feature_columns:
            raise RuntimeError("Model preprocessor/metadata missing. Run `python -m ml.train` first.")

    def _build_feature_matrix(self, df: pd.DataFrame) -> pd.DataFrame:
        engineered_df = engineer_features_df(df)
        transformed_df = self.preprocessor.transform(engineered_df)
        for col in self.final_feature_columns:
            if col not in transformed_df.columns:
                transformed_df[col] = 0.0
        return transformed_df[self.final_feature_columns].astype(float)

    def get_prediction_options(self) -> Dict[str, List[str]]:
        self._ensure_model_loaded()
        return {
            "sectors": self.categories_map.get("Sector", []),
            "industry_sectors": self.categories_map.get("Industry_Sectors", []),
            "transport_modes": self.categories_map.get("Supply_Chain_Transport_Mode", []),
        }

    def predict(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        self._ensure_model_loaded()

        total_energy = float(input_data.get("Total_Energy_Consumption_kWh", input_data.get("total_energy", 0.0)))
        renewable_energy = float(input_data.get("Renewable_Energy_Consumption_kWh", input_data.get("renewable_energy", 0.0)))
        nonrenewable_energy = float(input_data.get("NonRenewable_Energy_Consumption_kWh", input_data.get("nonrenewable_energy", 0.0)))
        production_output = float(input_data.get("Production_Output_Units", input_data.get("production_output", 0.0)))
        transport_distance = float(input_data.get("Supply_Chain_Transport_km", input_data.get("transport_distance", 0.0)))
        raw_material_usage = float(input_data.get("Raw_Material_Usage_kg", input_data.get("raw_material_usage", 0.0)))
        employment_count = float(input_data.get("Employment_Count", input_data.get("employment_count", 0.0)))

        sector = input_data.get("Sector", input_data.get("sector"))
        industry_sector = input_data.get("Industry_Sectors", input_data.get("industry_sector"))
        transport_mode = input_data.get("Supply_Chain_Transport_Mode", input_data.get("transport_mode"))

        numeric_values = {
            "Total_Energy_Consumption_kWh": total_energy,
            "Renewable_Energy_Consumption_kWh": renewable_energy,
            "NonRenewable_Energy_Consumption_kWh": nonrenewable_energy,
            "Production_Output_Units": production_output,
            "Supply_Chain_Transport_km": transport_distance,
            "Raw_Material_Usage_kg": raw_material_usage,
            "Employment_Count": employment_count,
        }
        for name, val in numeric_values.items():
            if not np.isfinite(val):
                raise ValueError(f"{name} must contain a valid number.")
            if val < 0:
                raise ValueError(f"{name} cannot be negative.")

        row = dict(numeric_values)
        if sector:
            row["Sector"] = str(sector).strip()
        if industry_sector:
            row["Industry_Sectors"] = str(industry_sector).strip()
        if transport_mode:
            row["Supply_Chain_Transport_Mode"] = str(transport_mode).strip()

        X = self._build_feature_matrix(pd.DataFrame([row]))
        prediction = float(self.model.predict(X)[0])

        analytics = calculate_post_prediction_features(
            predicted_co2=prediction,
            production_output=production_output,
            total_energy=total_energy,
            employment_count=employment_count,
            renewable_energy=renewable_energy,
            nonrenewable_energy=nonrenewable_energy,
        )

        return {
            "predicted_co2": prediction,
            "carbon_intensity": analytics["carbon_intensity"],
            "energy_per_employee": analytics["energy_per_employee"],
            "renewable_energy_ratio": analytics["renewable_energy_ratio"],
            "nonrenewable_energy_ratio": analytics["nonrenewable_energy_ratio"],
            "sector": row.get("Sector"),
            "industry_sector": row.get("Industry_Sectors"),
            "transport_mode": row.get("Supply_Chain_Transport_Mode"),
        }

    def predict_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        self._ensure_model_loaded()
        if df.empty:
            raise ValueError("Dataset is empty.")

        missing = [col for col in RAW_NUMERIC_COLUMNS if col not in df.columns]
        if missing:
            raise ValueError("Missing required columns: " + ", ".join(missing))

        working_df = df.copy()
        for col in RAW_NUMERIC_COLUMNS:
            working_df[col] = pd.to_numeric(working_df[col], errors="coerce")

        if working_df[RAW_NUMERIC_COLUMNS].isna().any().any():
            raise ValueError("Dataset contains missing or invalid model feature values.")

        X = self._build_feature_matrix(working_df)
        predictions = self.model.predict(X)

        result_df = working_df.copy()
        result_df["Predicted_Carbon_Emission_tCO2e"] = predictions

        result_df["Carbon_Intensity"] = np.where(
            result_df["Production_Output_Units"] > 0,
            result_df["Predicted_Carbon_Emission_tCO2e"] / result_df["Production_Output_Units"],
            0.0,
        )
        result_df["Energy_Per_Employee"] = np.where(
            result_df["Employment_Count"] > 0,
            result_df["Total_Energy_Consumption_kWh"] / result_df["Employment_Count"],
            0.0,
        )
        result_df["Renewable_Energy_Ratio"] = np.where(
            result_df["Total_Energy_Consumption_kWh"] > 0,
            result_df["Renewable_Energy_Consumption_kWh"] / result_df["Total_Energy_Consumption_kWh"],
            0.0,
        )
        return result_df

    def get_feature_importance(self) -> List[Dict[str, Any]]:
        return self.feature_importance

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "model_loaded": self.model is not None,
            "model_type": type(self.model).__name__ if self.model is not None else None,
            "features": self.final_feature_columns,
            "categories_map": self.categories_map,
            "metadata": self.metadata,
            "feature_importance": self.feature_importance,
        }


model_service = ModelService()