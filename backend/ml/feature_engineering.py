"""
Operational Feature Engineering for CarbonAI.
Computes non-leaking physical ratios and operational intensity metrics.
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np

ENGINEERED_FEATURE_NAMES = [
    "Renewable_Energy_Share",
    "NonRenewable_Energy_Share",
    "Energy_Per_Production",
    "NRE_Per_Production",
    "Transport_Intensity",
    "Raw_Material_Intensity",
    "Energy_Per_Employee"
]


def engineer_features_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies non-leaking physical feature engineering to a pandas DataFrame.
    Guarantees safe division by protecting against zero and negative values.
    """
    df_out = df.copy()

    # Total energy baseline for share calculations
    total_energy_safe = df_out["Total_Energy_Consumption_kWh"].astype(float).clip(lower=1.0)
    production_safe = df_out["Production_Output_Units"].astype(float).clip(lower=1.0)
    employment_safe = df_out["Employment_Count"].astype(float).clip(lower=1.0)

    # 1. Renewable and Non-Renewable Energy Mix Shares (0.0 to 1.0)
    df_out["Renewable_Energy_Share"] = (
        df_out["Renewable_Energy_Consumption_kWh"].astype(float) / total_energy_safe
    ).clip(lower=0.0, upper=1.0)

    df_out["NonRenewable_Energy_Share"] = (
        df_out["NonRenewable_Energy_Consumption_kWh"].astype(float) / total_energy_safe
    ).clip(lower=0.0, upper=1.0)

    # 2. Energy Intensities per Unit Production
    df_out["Energy_Per_Production"] = (
        df_out["Total_Energy_Consumption_kWh"].astype(float) / production_safe
    )

    df_out["NRE_Per_Production"] = (
        df_out["NonRenewable_Energy_Consumption_kWh"].astype(float) / production_safe
    )

    # 3. Supply Chain Transport Intensity (km / production unit)
    df_out["Transport_Intensity"] = (
        df_out["Supply_Chain_Transport_km"].astype(float) / production_safe
    )

    # 4. Raw Material Intensity (kg / production unit)
    df_out["Raw_Material_Intensity"] = (
        df_out["Raw_Material_Usage_kg"].astype(float) / production_safe
    )

    # 5. Energy per Employee (kWh / employee)
    df_out["Energy_Per_Employee"] = (
        df_out["Total_Energy_Consumption_kWh"].astype(float) / employment_safe
    )

    return df_out


def engineer_features_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Applies feature engineering to a single dictionary input for real-time inference.
    """
    total_energy = float(data.get("Total_Energy_Consumption_kWh", 0.0))
    renewable_energy = float(data.get("Renewable_Energy_Consumption_kWh", 0.0))
    non_renewable_energy = float(data.get("NonRenewable_Energy_Consumption_kWh", 0.0))
    production = float(data.get("Production_Output_Units", 0.0))
    transport_km = float(data.get("Supply_Chain_Transport_km", 0.0))
    raw_material = float(data.get("Raw_Material_Usage_kg", 0.0))
    employment = float(data.get("Employment_Count", 0.0))

    # Safe denominators
    total_energy_safe = max(total_energy, 1.0)
    production_safe = max(production, 1.0)
    employment_safe = max(employment, 1.0)

    # If renewable is missing but total and NRE exist, derive it
    if "Renewable_Energy_Consumption_kWh" not in data and "Total_Energy_Consumption_kWh" in data and "NonRenewable_Energy_Consumption_kWh" in data:
        renewable_energy = max(0.0, total_energy - non_renewable_energy)

    data_out = dict(data)
    data_out["Renewable_Energy_Consumption_kWh"] = renewable_energy
    data_out["Renewable_Energy_Share"] = min(1.0, max(0.0, renewable_energy / total_energy_safe))
    data_out["NonRenewable_Energy_Share"] = min(1.0, max(0.0, non_renewable_energy / total_energy_safe))
    data_out["Energy_Per_Production"] = total_energy / production_safe
    data_out["NRE_Per_Production"] = non_renewable_energy / production_safe
    data_out["Transport_Intensity"] = transport_km / production_safe
    data_out["Raw_Material_Intensity"] = raw_material / production_safe
    data_out["Energy_Per_Employee"] = total_energy / employment_safe

    return data_out


def calculate_post_prediction_features(
    predicted_co2: float,
    production_output: float,
    total_energy: float,
    employment_count: float
) -> Dict[str, float]:
    """
    Computes dashboard presentation metrics from predicted emissions.
    Retains full backward-compatibility with backend/feature_engineering.py.
    """
    production_safe = max(production_output, 1.0)
    employment_safe = max(employment_count, 1.0)

    carbon_intensity = predicted_co2 / production_safe
    energy_per_employee = total_energy / employment_safe

    return {
        "carbon_intensity": float(carbon_intensity),
        "energy_per_employee": float(energy_per_employee)
    }
