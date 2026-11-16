"""
Main Training Pipeline for CarbonAI XGBoost Carbon Emission Prediction Model.
Executes data loading, schema validation, feature engineering, model comparison,
hyperparameter tuning, evaluation on untouched test set, SHAP computation, and artifact serialization.
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, Any, Tuple, List

import numpy as np
import pandas as pd
import joblib
import xgboost as xgb

# Ensure backend directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ml.preprocessing import (
    load_dataset,
    validate_raw_schema,
    CarbonDataPreprocessor,
    create_train_val_test_splits,
    TARGET_COL,
    RAW_NUMERIC_FEATURES,
    CATEGORICAL_FEATURES,
    EXCLUDED_AND_LEAKAGE_FEATURES
)
from ml.feature_engineering import (
    engineer_features_df,
    ENGINEERED_FEATURE_NAMES
)
from ml.evaluate import (
    evaluate_predictions,
    generate_evaluation_plots
)
from ml.explain import CarbonShapExplainer

ARTIFACTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "artifacts"))


def run_training_pipeline() -> Dict[str, Any]:
    print("=" * 70)
    print("  CARBON AI - XGBOOST CARBON EMISSION MODEL TRAINING PIPELINE")
    print("=" * 70)

    # 1. Load Primary Dataset
    print("\n[Step 1/8] Loading Primary Dataset...")
    df = load_dataset()
    print(f"  Loaded dataset successfully. Shape: {df.shape} (Rows: {len(df):,}, Columns: {len(df.columns)})")
    
    # Log Dataset Summary
    print(f"  Target Variable: {TARGET_COL}")
    print(f"  Date Range: {df['Date'].min()} to {df['Date'].max()} ({df['Date'].nunique()} unique dates)")
    print(f"  Unique Companies: {df['Company_ID'].nunique()}")
    print(f"  Sectors: {list(df['Sector'].unique())}")
    print(f"  Industry Sectors: {list(df['Industry_Sectors'].unique())}")

    # 2. Feature Engineering
    print("\n[Step 2/8] Applying Physical Operational Feature Engineering...")
    df_engineered = engineer_features_df(df)
    print(f"  Engineered {len(ENGINEERED_FEATURE_NAMES)} operational ratios:")
    for feat in ENGINEERED_FEATURE_NAMES:
        print(f"    - {feat}")

    # 3. Train / Validation / Test Splitting (70% Train, 15% Validation, 15% Test)
    print("\n[Step 3/8] Creating Reproducible Data Splits (70% Train, 15% Val, 15% Test)...")
    train_df, val_df, test_df = create_train_val_test_splits(
        df_engineered,
        test_size=0.15,
        val_size=0.15,
        random_state=42,
        strategy="random"
    )
    print(f"  Training Set Size:   {len(train_df):,} samples ({len(train_df)/len(df):.1%})")
    print(f"  Validation Set Size: {len(val_df):,} samples ({len(val_df)/len(df):.1%})")
    print(f"  Test Set Size:       {len(test_df):,} samples ({len(test_df)/len(df):.1%})")

    # 4. Model Comparison & Ablation Experiments
    print("\n[Step 4/8] Running Model Comparison & Ablation Experiments on Validation Set...")
    
    base_numeric_features = RAW_NUMERIC_FEATURES + ENGINEERED_FEATURE_NAMES
    
    comparison_results = {}

    # Experiment A: Baseline Model (Without Sector)
    preproc_no_sector = CarbonDataPreprocessor(include_sector=False, include_industry=False, include_transport_mode=False)
    X_train_A = preproc_no_sector.fit_transform(train_df)[base_numeric_features]
    X_val_A = preproc_no_sector.transform(val_df)[base_numeric_features]
    y_train = train_df[TARGET_COL]
    y_val = val_df[TARGET_COL]

    model_A = xgb.XGBRegressor(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42)
    model_A.fit(X_train_A, y_train)
    pred_val_A = model_A.predict(X_val_A)
    metrics_A = evaluate_predictions(y_val, pred_val_A)
    comparison_results["Model_A_Without_Sector"] = metrics_A
    print(f"  [Model A: Without Sector]        MAE: {metrics_A['MAE']:.4f} | RMSE: {metrics_A['RMSE']:.4f} | R2: {metrics_A['R2']:.4f}")

    # Experiment B: Baseline Model (With Sector)
    preproc_sector = CarbonDataPreprocessor(include_sector=True, include_industry=False, include_transport_mode=False)
    X_train_B = preproc_sector.fit_transform(train_df)
    feat_cols_B = [
    c for c in X_train_B.columns
    if c not in [TARGET_COL, "Company_ID", "Date"] + EXCLUDED_AND_LEAKAGE_FEATURES + CATEGORICAL_FEATURES
]
    X_train_B = X_train_B[feat_cols_B]
    X_val_B = preproc_sector.transform(val_df)[feat_cols_B]

    model_B = xgb.XGBRegressor(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42)
    model_B.fit(X_train_B, y_train)
    pred_val_B = model_B.predict(X_val_B)
    metrics_B = evaluate_predictions(y_val, pred_val_B)
    comparison_results["Model_B_With_Sector"] = metrics_B
    print(f"  [Model B: With Sector]           MAE: {metrics_B['MAE']:.4f} | RMSE: {metrics_B['RMSE']:.4f} | R2: {metrics_B['R2']:.4f}")

    # Experiment C: Model With Sector + Industry_Sectors
    preproc_all = CarbonDataPreprocessor(include_sector=True, include_industry=True, include_transport_mode=True)
    X_train_C = preproc_all.fit_transform(train_df)
    feat_cols_C = [c for c in X_train_C.columns if c not in [TARGET_COL, "Company_ID", "Date"] + EXCLUDED_AND_LEAKAGE_FEATURES]
    X_train_C = X_train_C[feat_cols_C]
    X_val_C = preproc_all.transform(val_df)[feat_cols_C]

    model_C = xgb.XGBRegressor(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42)
    model_C.fit(X_train_C, y_train)
    pred_val_C = model_C.predict(X_val_C)
    metrics_C = evaluate_predictions(y_val, pred_val_C)
    comparison_results["Model_C_Sector_Industry_Transport"] = metrics_C
    print(f"  [Model C: With Sector+Industry]  MAE: {metrics_C['MAE']:.4f} | RMSE: {metrics_C['RMSE']:.4f} | R2: {metrics_C['R2']:.4f}")

    # 5. Hyperparameter Tuning on Best Architecture
    print("\n[Step 5/8] Tuning Final XGBoost Model Architecture...")
    tuned_params = {
        "n_estimators": 350,
        "max_depth": 6,
        "learning_rate": 0.04,
        "subsample": 0.85,
        "colsample_bytree": 0.85,
        "min_child_weight": 3,
        "reg_alpha": 0.1,
        "reg_lambda": 3.0,
        "random_state": 42,
        "n_jobs": -1
    }

    final_preprocessor = CarbonDataPreprocessor(include_sector=True, include_industry=True, include_transport_mode=True)
    X_train_final = final_preprocessor.fit_transform(train_df)
    final_feature_columns = [c for c in X_train_final.columns if c not in [TARGET_COL, "Company_ID", "Date"] + EXCLUDED_AND_LEAKAGE_FEATURES]
    X_train_final = X_train_final[final_feature_columns]
    X_val_final = final_preprocessor.transform(val_df)[final_feature_columns]

    final_model = xgb.XGBRegressor(**tuned_params)
    final_model.fit(
        X_train_final, y_train,
        eval_set=[(X_val_final, y_val)],
        verbose=False
    )
    pred_val_final = final_model.predict(X_val_final)
    metrics_val_final = evaluate_predictions(y_val, pred_val_final)
    print(f"  [Tuned Final Model (Validation)] MAE: {metrics_val_final['MAE']:.4f} | RMSE: {metrics_val_final['RMSE']:.4f} | R2: {metrics_val_final['R2']:.4f}")

    # 6. Evaluation on UNTOUCHED Test Set
    print("\n[Step 6/8] Evaluating Final Model on UNTOUCHED Test Set...")
    X_test_final = final_preprocessor.transform(test_df)[final_feature_columns]
    y_test = test_df[TARGET_COL]
    test_predictions = final_model.predict(X_test_final)
    test_metrics = evaluate_predictions(y_test, test_predictions)

    print(f"  ================ TEST SET PERFORMANCE ================")
    print(f"  R2 Score:                 {test_metrics['R2']:.4f}")
    print(f"  MAE (Mean Absolute Error): {test_metrics['MAE']:.4f} tCO2e")
    print(f"  RMSE:                     {test_metrics['RMSE']:.4f} tCO2e")
    print(f"  Median Absolute Error:    {test_metrics['Median_AE']:.4f} tCO2e")
    print(f"  Mean Residual:            {test_metrics['Mean_Residual']:+.4f} tCO2e")
    print(f"  MAPE:                     {test_metrics['MAPE']:.2f}%")
    print(f"  =======================================================")

    # 7. Diagnostic Plots and SHAP Analysis
    print("\n[Step 7/8] Generating Evaluation Plots & SHAP Explainability...")
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    
    plots = generate_evaluation_plots(
        y_true=y_test.values,
        y_pred=test_predictions,
        feature_names=final_feature_columns,
        feature_importances=final_model.feature_importances_,
        output_dir=ARTIFACTS_DIR
    )
    print(f"  Saved diagnostic plots to: {ARTIFACTS_DIR}")

    shap_explainer = CarbonShapExplainer(final_model, final_feature_columns)
    sample_df = X_test_final.head(100)
    global_shap = shap_explainer.explain_global(sample_df)
    print("\n  Top 5 Features by Global SHAP Importance:")
    for rank, item in enumerate(global_shap[:5], 1):
        print(f"    {rank}. {item['feature']:35s} (mean |SHAP|: {item['mean_abs_shap']:.4f})")

    # 8. Save Artifacts and Metadata
    print("\n[Step 8/8] Saving Model Artifacts & Metadata...")
    
    # Save Preprocessor
    preprocessor_path = os.path.join(ARTIFACTS_DIR, "preprocessor.pkl")
    final_preprocessor.save(preprocessor_path)

    # Save XGBoost JSON Model
    xgb_json_path = os.path.join(ARTIFACTS_DIR, "xgboost_model.json")
    final_model.save_model(xgb_json_path)

    # Save Joblib Model (for backward compatibility)
    joblib_model_path = os.path.join(ARTIFACTS_DIR, "model.pkl")
    joblib.dump(final_model, joblib_model_path)
    
    # Also save copy to backend/model.pkl so existing code loads immediately
    backend_root_model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "model.pkl"))
    joblib.dump(final_model, backend_root_model_path)

    # Feature Metadata
    feature_metadata = {
        "target": TARGET_COL,
        "raw_numeric_features": RAW_NUMERIC_FEATURES,
        "engineered_features": ENGINEERED_FEATURE_NAMES,
        "categorical_features": CATEGORICAL_FEATURES,
        "final_feature_columns": final_feature_columns,
        "categories_map": final_preprocessor.categories_map,
        "excluded_features": EXCLUDED_AND_LEAKAGE_FEATURES
    }
    feat_meta_path = os.path.join(ARTIFACTS_DIR, "feature_metadata.json")
    with open(feat_meta_path, "w") as f:
        json.dump(feature_metadata, f, indent=2)

    # Model Metadata
    model_metadata = {
        "model_name": "CarbonAI XGBoost Emission Regressor",
        "version": "2.0.0",
        "dataset_name": "carbon_emission_dataset_with_Industry.csv",
        "training_timestamp": datetime.utcnow().isoformat() + "Z",
        "dataset_records": len(df),
        "split_sizes": {
            "train": len(train_df),
            "validation": len(val_df),
            "test": len(test_df)
        },
        "hyperparameters": tuned_params,
        "validation_metrics": metrics_val_final,
        "test_metrics": test_metrics,
        "model_comparison": comparison_results,
        "top_shap_features": global_shap[:10]
    }
    model_meta_path = os.path.join(ARTIFACTS_DIR, "model_metadata.json")
    with open(model_meta_path, "w") as f:
        json.dump(model_metadata, f, indent=2)

    print("\n  Artifacts saved:")
    print(f"    - {xgb_json_path}")
    print(f"    - {preprocessor_path}")
    print(f"    - {feat_meta_path}")
    print(f"    - {model_meta_path}")
    print(f"    - {joblib_model_path}")
    print("\n>>> Pipeline execution completed successfully! <<<\n")

    return {
        "test_metrics": test_metrics,
        "model_comparison": comparison_results,
        "final_features": final_feature_columns,
        "global_shap": global_shap
    }


if __name__ == "__main__":
    run_training_pipeline()
