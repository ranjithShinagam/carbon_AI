"""
Data preprocessing, schema validation, and categorical encoding module for CarbonAI.
"""

import os
from typing import Dict, List, Optional, Tuple, Union
import pandas as pd
import numpy as np
import joblib

# Constant Definitions
TARGET_COL = "Carbon_Emission_tCO2e_TARGET"

RAW_NUMERIC_FEATURES = [
    "Total_Energy_Consumption_kWh",
    "Renewable_Energy_Consumption_kWh",
    "NonRenewable_Energy_Consumption_kWh",
    "Production_Output_Units",
    "Supply_Chain_Transport_km",
    "Raw_Material_Usage_kg",
    "Employment_Count",
]

CATEGORICAL_FEATURES = [
    "Sector",
    "Industry_Sectors",
    "Supply_Chain_Transport_Mode"
]

# Features excluded from ML due to target leakage or post-prediction advisory nature
EXCLUDED_AND_LEAKAGE_FEATURES = [
    "Carbon_Tax_USD",                     # LEAKAGE: Derived directly from observed emission * tax rate
    "Carbon_Reduction_Strategy",           # ADVISORY: Strategic mitigation decision made after prediction
    "Strategy_Implementation_Cost_USD",   # ADVISORY: Financial CapEx for future mitigation project
    "Expected_Carbon_Reduction_Percent",   # ADVISORY: Target reduction percentage for strategic planning
    "Expected_Renewable_Share_Percent",   # ADVISORY: Future target renewable share goal
    "Energy_Cost_USD",                    # FINANCIAL: Financial billing variable, not physical driver
    "Public_Acceptance_Index",            # ESG METRIC: External perception index
    "Social_Impact_Score",                # ESG METRIC: External social rating
    "Process_Efficiency_Percent",         # OPERATIONAL: Secondary process metric
    "Company_ID",                         # IDENTIFIER: Entity identifier (used for analytics/grouping)
    "Date"                                # TEMPORAL: Time stamp (used for time-series analytics)
]

POSSIBLE_DATASET_PATHS = [
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "carbon_emission_dataset_with_Industry.csv"),
    os.path.join(os.path.dirname(__file__), "..", "carbon_emission_dataset_with_Industry.csv"),
    os.path.join(os.getcwd(), "data", "carbon_emission_dataset_with_Industry.csv"),
    os.path.join(os.getcwd(), "backend", "carbon_emission_dataset_with_Industry.csv"),
    os.path.join(os.getcwd(), "carbon_emission_dataset_with_Industry.csv"),
]


def find_dataset_path() -> str:
    """Locates the primary dataset in the workspace."""
    for path in POSSIBLE_DATASET_PATHS:
        normalized = os.path.abspath(path)
        if os.path.exists(normalized):
            return normalized
    raise FileNotFoundError(
        f"Could not locate 'carbon_emission_dataset_with_Industry.csv'. Checked: {POSSIBLE_DATASET_PATHS}"
    )


def load_dataset(filepath: Optional[str] = None) -> pd.DataFrame:
    """
    Loads the primary carbon emission dataset without modifying the underlying file.
    """
    if filepath is None:
        filepath = find_dataset_path()
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Dataset file not found at {filepath}")
    
    df = pd.read_csv(filepath)
    validate_raw_schema(df)
    return df


def validate_raw_schema(df: pd.DataFrame) -> bool:
    """
    Validates that the input dataframe contains all required fields and the target.
    """
    required_cols = RAW_NUMERIC_FEATURES + [TARGET_COL]
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Dataset is missing required columns: {missing}")
    
    if df[TARGET_COL].isnull().any():
        raise ValueError(f"Target column '{TARGET_COL}' contains null values.")
    
    return True


class CarbonDataPreprocessor:
    """
    Handles categorical encoding, feature column alignment, and preprocessing.
    """
    def __init__(self, include_sector: bool = True, include_industry: bool = True, include_transport_mode: bool = True):
        self.include_sector = include_sector
        self.include_industry = include_industry
        self.include_transport_mode = include_transport_mode
        self.categorical_cols: List[str] = []
        if self.include_sector:
            self.categorical_cols.append("Sector")
        if self.include_industry:
            self.categorical_cols.append("Industry_Sectors")
        if self.include_transport_mode:
            self.categorical_cols.append("Supply_Chain_Transport_Mode")
            
        self.categories_map: Dict[str, List[str]] = {}
        self.feature_names_out: List[str] = []
        self.is_fitted = False

    def fit(self, df: pd.DataFrame) -> "CarbonDataPreprocessor":
        """Learns categorical categories and computes expected output schema."""
        self.categories_map = {}
        for col in self.categorical_cols:
            if col in df.columns:
                # Store sorted unique categories
                unique_vals = sorted([str(x) for x in df[col].dropna().unique()])
                self.categories_map[col] = unique_vals
            else:
                self.categories_map[col] = []
        
        self.is_fitted = True
        return self

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transforms numerical and categorical features into a clean modeling matrix.
        """
        if not self.is_fitted:
            raise RuntimeError("Preprocessor must be fitted before transforming data.")
        
        df_out = df.copy()
        
        # One-hot encode configured categorical columns
        for col in self.categorical_cols:
            if col in df_out.columns and col in self.categories_map:
                for cat in self.categories_map[col]:
                    col_name = f"{col}_{cat}"
                    df_out[col_name] = (df_out[col].astype(str) == cat).astype(float)
                # Drop original raw categorical column
                df_out = df_out.drop(columns=[col])
            else:
                # If categorical column is missing at inference, populate zeros
                for cat in self.categories_map.get(col, []):
                    col_name = f"{col}_{cat}"
                    df_out[col_name] = 0.0
                    
        return df_out

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        return self.fit(df).transform(df)

    def save(self, filepath: str) -> None:
        """Serializes the preprocessor."""
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        joblib.dump(self, filepath)

    @classmethod
    def load(cls, filepath: str) -> "CarbonDataPreprocessor":
        """Loads serialized preprocessor."""
        return joblib.load(filepath)


def create_train_val_test_splits(
    df: pd.DataFrame,
    test_size: float = 0.15,
    val_size: float = 0.15,
    random_state: int = 42,
    strategy: str = "random"
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Creates reproducible Train, Validation, and Test splits.
    
    Parameters:
        df: Input DataFrame
        test_size: Proportion of dataset for test set (default 0.15)
        val_size: Proportion of dataset for validation set (default 0.15)
        random_state: Random seed for reproducibility
        strategy: 'random' or 'chronological'
        
    Returns:
        (train_df, val_df, test_df)
    """
    if strategy == "chronological" and "Date" in df.columns:
        df_sorted = df.sort_values("Date").reset_index(drop=True)
        n = len(df_sorted)
        n_test = int(n * test_size)
        n_val = int(n * val_size)
        n_train = n - n_test - n_val
        
        train_df = df_sorted.iloc[:n_train].copy()
        val_df = df_sorted.iloc[n_train:n_train + n_val].copy()
        test_df = df_sorted.iloc[n_train + n_val:].copy()
    else:
        # Random split
        from sklearn.model_selection import train_test_split
        total_eval_size = test_size + val_size
        train_df, temp_df = train_test_split(df, test_size=total_eval_size, random_state=random_state)
        relative_test_ratio = test_size / total_eval_size
        val_df, test_df = train_test_split(temp_df, test_size=relative_test_ratio, random_state=random_state)
        
    return train_df.reset_index(drop=True), val_df.reset_index(drop=True), test_df.reset_index(drop=True)
