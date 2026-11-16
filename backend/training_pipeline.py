# ============================================================
# Carbon AI - XGBoost Carbon Emission Training Pipeline
# ============================================================

import os
import json
import joblib
import warnings
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split, RandomizedSearchCV, KFold
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor

warnings.filterwarnings("ignore")


# ============================================================
# 1. CONFIGURATION
# ============================================================

DATASET_PATH = "carbon_emission_dataset_with_Industry.csv"

TARGET = "Carbon_Emission_tCO2e_TARGET"

MODEL_FILE = "model.pkl"
METADATA_FILE = "model_metadata.json"
IMPORTANCE_FILE = "feature_importance.csv"

RANDOM_STATE = 42


# ============================================================
# 2. FEATURES
# ============================================================

BASE_FEATURES = [
    "Total_Energy_Consumption_kWh",
    "NonRenewable_Energy_Consumption_kWh",
    "Renewable_Energy_Consumption_kWh",
    "Production_Output_Units",
    "Supply_Chain_Transport_km",
    "Raw_Material_Usage_kg",
    "Employment_Count",
]

ENGINEERED_FEATURES = [
    "NonRenewable_Energy_Ratio",
]

MODEL_FEATURES = BASE_FEATURES + ENGINEERED_FEATURES


# ============================================================
# 3. LOAD DATASET
# ============================================================

if not os.path.exists(DATASET_PATH):
    raise FileNotFoundError(
        f"""
Dataset not found: {DATASET_PATH}

Place the dataset inside the backend directory.
"""
    )

df = pd.read_csv(DATASET_PATH)

print("=" * 70)
print("CARBON AI - XGBOOST TRAINING")
print("=" * 70)

print(f"\nDataset shape: {df.shape}")

print("\nDataset columns:")
for column in df.columns:
    print(f" - {column}")


# ============================================================
# 4. VALIDATE REQUIRED COLUMNS
# ============================================================

required_columns = BASE_FEATURES + [TARGET]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        "\nMissing required columns:\n"
        + "\n".join(
            f" - {column}"
            for column in missing_columns
        )
    )

print("\nAll required columns are present.")


# ============================================================
# 5. REMOVE DUPLICATES
# ============================================================

initial_rows = len(df)

df = df.drop_duplicates().reset_index(drop=True)

duplicates_removed = initial_rows - len(df)

print(
    f"\nDuplicate rows removed: "
    f"{duplicates_removed}"
)


# ============================================================
# 6. CONVERT NUMERIC COLUMNS
# ============================================================

for column in required_columns:

    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )


# ============================================================
# 7. HANDLE MISSING VALUES
# ============================================================

# Target cannot be missing.

df = df.dropna(
    subset=[TARGET]
).reset_index(drop=True)


# Fill missing feature values using median.

for column in BASE_FEATURES:

    if df[column].isna().any():

        median_value = df[column].median()

        df[column] = df[column].fillna(
            median_value
        )


print(
    f"Rows available for training: "
    f"{len(df)}"
)


# ============================================================
# 8. DATA VALIDATION
# ============================================================

print("\nChecking negative values...")

for column in BASE_FEATURES + [TARGET]:

    negative_count = int(
        (df[column] < 0).sum()
    )

    if negative_count > 0:

        print(
            f"WARNING: {column} contains "
            f"{negative_count} negative values."
        )


# ============================================================
# 9. ENERGY CONSISTENCY CHECK
# ============================================================

energy_sum = (
    df["Renewable_Energy_Consumption_kWh"]
    +
    df["NonRenewable_Energy_Consumption_kWh"]
)

energy_difference = (
    df["Total_Energy_Consumption_kWh"]
    -
    energy_sum
).abs()

print(
    "\nMedian difference between "
    "Total Energy and "
    "(Renewable + NonRenewable):",
    round(
        float(
            energy_difference.median()
        ),
        4
    )
)


# ============================================================
# 10. FEATURE ENGINEERING
# ============================================================

df["NonRenewable_Energy_Ratio"] = np.where(

    df["Total_Energy_Consumption_kWh"] > 0,

    df["NonRenewable_Energy_Consumption_kWh"]
    /
    df["Total_Energy_Consumption_kWh"],

    0.0
)


# Handle infinite values.

df.replace(
    [np.inf, -np.inf],
    np.nan,
    inplace=True
)

df["NonRenewable_Energy_Ratio"] = (
    df["NonRenewable_Energy_Ratio"]
    .fillna(0.0)
)


# ============================================================
# 11. FEATURE / TARGET SELECTION
# ============================================================

X = df[
    MODEL_FEATURES
].copy()

y = df[
    TARGET
].copy()


print("\nModel features:")

for feature in MODEL_FEATURES:

    print(
        f" - {feature}"
    )

print(
    f"\nTarget: {TARGET}"
)


# ============================================================
# IMPORTANT EXCLUDED COLUMNS
# ============================================================

# Company_ID
# -> identifier only
#
# Carbon_Tax_USD
# -> potential target leakage
#
# Sector
# -> used later for sector analytics
#
# Industry_Sectors
# -> used later for sector analytics
#
# Carbon_Reduction_Strategy
# -> strategy information
#
# Expected_Carbon_Reduction_Percent
# -> potentially future information
#
# Expected_Renewable_Share_Percent
# -> potentially future information
#
# Strategy_Implementation_Cost_USD
# -> strategy information


# ============================================================
# 12. TRAIN / VALIDATION / TEST SPLIT
# ============================================================

# 15% untouched final test set.

X_train_valid, X_test, y_train_valid, y_test = (
    train_test_split(
        X,
        y,
        test_size=0.15,
        random_state=RANDOM_STATE
    )
)


# Approximately 15% of the complete dataset
# becomes validation data.

X_train, X_valid, y_train, y_valid = (
    train_test_split(
        X_train_valid,
        y_train_valid,
        test_size=0.1764705882,
        random_state=RANDOM_STATE
    )
)


print("\nData split:")

print(
    f"Training   : {len(X_train)}"
)

print(
    f"Validation : {len(X_valid)}"
)

print(
    f"Test       : {len(X_test)}"
)


# ============================================================
# 13. BASELINE MODEL
# ============================================================

baseline_model = XGBRegressor(

    objective="reg:squarederror",

    eval_metric="rmse",

    tree_method="hist",

    n_estimators=300,

    max_depth=6,

    learning_rate=0.05,

    subsample=0.9,

    colsample_bytree=0.9,

    random_state=RANDOM_STATE,

    n_jobs=-1
)


print(
    "\nTraining baseline model..."
)


baseline_model.fit(
    X_train,
    y_train
)


baseline_predictions = (
    baseline_model.predict(
        X_valid
    )
)


baseline_r2 = r2_score(
    y_valid,
    baseline_predictions
)

baseline_mae = mean_absolute_error(
    y_valid,
    baseline_predictions
)

baseline_rmse = np.sqrt(
    mean_squared_error(
        y_valid,
        baseline_predictions
    )
)


print(
    "\nBaseline validation performance:"
)

print(
    f"R2   : {baseline_r2:.6f}"
)

print(
    f"MAE  : {baseline_mae:.6f}"
)

print(
    f"RMSE : {baseline_rmse:.6f}"
)


# ============================================================
# 14. HYPERPARAMETER SEARCH
# ============================================================

xgb = XGBRegressor(

    objective="reg:squarederror",

    eval_metric="rmse",

    tree_method="hist",

    random_state=RANDOM_STATE,

    n_jobs=1
)


parameter_space = {

    "n_estimators": [
        300,
        500,
        700,
        900,
        1200
    ],

    "max_depth": [
        3,
        4,
        5,
        6,
        7,
        8
    ],

    "learning_rate": [
        0.01,
        0.02,
        0.03,
        0.05,
        0.08,
        0.1
    ],

    "min_child_weight": [
        1,
        3,
        5,
        7,
        10
    ],

    "subsample": [
        0.7,
        0.8,
        0.9,
        1.0
    ],

    "colsample_bytree": [
        0.7,
        0.8,
        0.9,
        1.0
    ],

    "gamma": [
        0.0,
        0.05,
        0.1,
        0.2,
        0.5
    ],

    "reg_alpha": [
        0.0,
        0.001,
        0.01,
        0.1,
        1.0
    ],

    "reg_lambda": [
        0.5,
        1.0,
        2.0,
        5.0,
        10.0
    ]
}


cv = KFold(

    n_splits=5,

    shuffle=True,

    random_state=RANDOM_STATE
)


search = RandomizedSearchCV(

    estimator=xgb,

    param_distributions=parameter_space,

    n_iter=40,

    scoring="neg_root_mean_squared_error",

    cv=cv,

    random_state=RANDOM_STATE,

    verbose=1,

    n_jobs=-1,

    refit=True
)


print(
    "\n"
    + "=" * 70
)

print(
    "RUNNING HYPERPARAMETER SEARCH"
)

print(
    "40 combinations × 5-fold CV"
)

print(
    "=" * 70
)


search.fit(
    X_train,
    y_train
)


# ============================================================
# 15. BEST PARAMETERS
# ============================================================

print(
    "\nBest parameters:"
)

for key, value in (
    search.best_params_.items()
):

    print(
        f"{key}: {value}"
    )


print(
    "\nBest CV RMSE:",
    -search.best_score_
)


# ============================================================
# 16. VALIDATION PERFORMANCE
# ============================================================

best_model = (
    search.best_estimator_
)


validation_predictions = (
    best_model.predict(
        X_valid
    )
)


validation_r2 = r2_score(
    y_valid,
    validation_predictions
)

validation_mae = mean_absolute_error(
    y_valid,
    validation_predictions
)

validation_rmse = np.sqrt(
    mean_squared_error(
        y_valid,
        validation_predictions
    )
)


print(
    "\nTuned validation performance:"
)

print(
    f"R2   : {validation_r2:.6f}"
)

print(
    f"MAE  : {validation_mae:.6f}"
)

print(
    f"RMSE : {validation_rmse:.6f}"
)


# ============================================================
# 17. FINAL MODEL
# ============================================================

# Retrain using training + validation data.
# The test set remains untouched.

final_model = XGBRegressor(

    objective="reg:squarederror",

    eval_metric="rmse",

    tree_method="hist",

    random_state=RANDOM_STATE,

    n_jobs=-1,

    **search.best_params_
)


print(
    "\nTraining final model..."
)


final_model.fit(

    X_train_valid,

    y_train_valid
)


# ============================================================
# 18. FINAL TEST EVALUATION
# ============================================================

test_predictions = (
    final_model.predict(
        X_test
    )
)


test_r2 = r2_score(
    y_test,
    test_predictions
)

test_mae = mean_absolute_error(
    y_test,
    test_predictions
)

test_rmse = np.sqrt(
    mean_squared_error(
        y_test,
        test_predictions
    )
)


# Training R2 for overfitting check.

train_predictions = (
    final_model.predict(
        X_train_valid
    )
)


train_r2 = r2_score(
    y_train_valid,
    train_predictions
)


print(
    "\n"
    + "=" * 70
)

print(
    "FINAL MODEL PERFORMANCE"
)

print(
    "=" * 70
)

print(
    f"Train R2 : {train_r2:.6f}"
)

print(
    f"Test R2  : {test_r2:.6f}"
)

print(
    f"R2 Gap   : "
    f"{abs(train_r2 - test_r2):.6f}"
)

print(
    f"Test MAE : {test_mae:.6f}"
)

print(
    f"Test RMSE: {test_rmse:.6f}"
)


# ============================================================
# 19. FEATURE IMPORTANCE
# ============================================================

importance_df = pd.DataFrame({

    "feature": MODEL_FEATURES,

    "importance":
        final_model.feature_importances_

})


importance_df = (
    importance_df
    .sort_values(
        "importance",
        ascending=False
    )
)


print(
    "\nFeature importance:"
)

print(
    importance_df.to_string(
        index=False
    )
)


importance_df.to_csv(

    IMPORTANCE_FILE,

    index=False
)


# ============================================================
# 20. SAVE MODEL
# ============================================================

joblib.dump(

    final_model,

    MODEL_FILE,

    compress=3
)


print(
    f"\nModel saved successfully: "
    f"{MODEL_FILE}"
)


# ============================================================
# 21. SAVE MODEL METADATA
# ============================================================

metadata = {

    "model_type":
        "XGBRegressor",

    "target":
        TARGET,

    "features":
        MODEL_FEATURES,

    "base_features":
        BASE_FEATURES,

    "engineered_features":
        ENGINEERED_FEATURES,

    "best_parameters":
        search.best_params_,

    "excluded_from_model": [

        "Company_ID",

        "Carbon_Tax_USD",

        "Sector",

        "Industry_Sectors",

        "Carbon_Reduction_Strategy",

        "Expected_Carbon_Reduction_Percent",

        "Expected_Renewable_Share_Percent",

        "Strategy_Implementation_Cost_USD"
    ],

    "metrics": {

        "baseline_validation_r2":
            float(baseline_r2),

        "baseline_validation_mae":
            float(baseline_mae),

        "baseline_validation_rmse":
            float(baseline_rmse),

        "validation_r2":
            float(validation_r2),

        "validation_mae":
            float(validation_mae),

        "validation_rmse":
            float(validation_rmse),

        "train_r2":
            float(train_r2),

        "test_r2":
            float(test_r2),

        "test_mae":
            float(test_mae),

        "test_rmse":
            float(test_rmse)
    }
}


with open(

    METADATA_FILE,

    "w",

    encoding="utf-8"

) as file:

    json.dump(

        metadata,

        file,

        indent=4
    )


print(
    f"Metadata saved: "
    f"{METADATA_FILE}"
)

print(
    f"Feature importance saved: "
    f"{IMPORTANCE_FILE}"
)


# ============================================================
# 22. SAMPLE PREDICTION
# ============================================================

sample = X_test.iloc[[0]]

sample_prediction = (
    final_model.predict(
        sample
    )[0]
)

sample_actual = (
    y_test.iloc[0]
)


print(
    "\nSample prediction:"
)

print(
    f"Predicted: "
    f"{sample_prediction:.4f} tCO2e"
)

print(
    f"Actual: "
    f"{sample_actual:.4f} tCO2e"
)


print(
    "\n"
    + "=" * 70
)

print(
    "TRAINING COMPLETED SUCCESSFULLY 🚀"
)

print(
    "=" * 70
)