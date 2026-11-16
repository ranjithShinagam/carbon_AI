"""
Model Evaluation and Diagnostics module for CarbonAI.
Computes evaluation metrics (MAE, RMSE, R2, median error, residuals) and diagnostic charts.
"""

from typing import Dict, Any, Tuple, Optional
import os
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, median_absolute_error
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns


def evaluate_predictions(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """
    Computes standard regression evaluation metrics and residual statistics.
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    residuals = y_true - y_pred

    mae = float(mean_absolute_error(y_true, y_pred))
    mse = float(mean_squared_error(y_true, y_pred))
    rmse = float(np.sqrt(mse))
    r2 = float(r2_score(y_true, y_pred))
    med_ae = float(median_absolute_error(y_true, y_pred))
    mean_res = float(np.mean(residuals))
    std_res = float(np.std(residuals))

    # Mean Absolute Percentage Error (handling zeros)
    non_zero = y_true != 0
    mape = float(np.mean(np.abs(residuals[non_zero] / y_true[non_zero])) * 100) if np.any(non_zero) else 0.0

    return {
        "MAE": mae,
        "MSE": mse,
        "RMSE": rmse,
        "R2": r2,
        "Median_AE": med_ae,
        "Mean_Residual": mean_res,
        "Std_Residual": std_res,
        "MAPE": mape
    }


def generate_evaluation_plots(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    feature_names: list,
    feature_importances: np.ndarray,
    output_dir: str
) -> Dict[str, str]:
    """
    Generates and saves diagnostic plots:
    1. Actual vs Predicted Scatter Plot
    2. Residual Distribution Plot
    3. Feature Importance Bar Chart
    """
    os.makedirs(output_dir, exist_ok=True)
    plot_paths = {}

    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    residuals = y_true - y_pred

    # 1. Actual vs Predicted Plot
    plt.figure(figsize=(8, 6))
    plt.scatter(y_true, y_pred, alpha=0.3, color="#39ff14", edgecolors="#0b1121", s=30)
    min_val = min(y_true.min(), y_pred.min())
    max_val = max(y_true.max(), y_pred.max())
    plt.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label="Ideal 1:1 Line")
    plt.xlabel("Actual Carbon Emission (tCO2e)")
    plt.ylabel("Predicted Carbon Emission (tCO2e)")
    plt.title("Actual vs Predicted Carbon Emissions")
    plt.legend()
    plt.tight_layout()
    actual_pred_path = os.path.join(output_dir, "actual_vs_predicted.png")
    plt.savefig(actual_pred_path, dpi=150)
    plt.close()
    plot_paths["actual_vs_predicted"] = actual_pred_path

    # 2. Residual Distribution Plot
    plt.figure(figsize=(8, 6))
    sns.histplot(residuals, kde=True, color="#3b82f6", bins=40)
    plt.axvline(0, color='r', linestyle='--', label="Zero Residual")
    plt.xlabel("Residual Error (Actual - Predicted) [tCO2e]")
    plt.ylabel("Frequency")
    plt.title("Prediction Residual Distribution")
    plt.legend()
    plt.tight_layout()
    residual_path = os.path.join(output_dir, "residual_distribution.png")
    plt.savefig(residual_path, dpi=150)
    plt.close()
    plot_paths["residual_distribution"] = residual_path

    # 3. Feature Importance Plot
    if feature_names is not None and feature_importances is not None:
        plt.figure(figsize=(10, max(6, len(feature_names) * 0.3)))
        feat_df = pd.DataFrame({
            "Feature": feature_names,
            "Importance": feature_importances
        }).sort_values("Importance", ascending=True).tail(15)

        plt.barh(feat_df["Feature"], feat_df["Importance"], color="#39ff14", edgecolor="#0b1121")
        plt.xlabel("Relative Importance Score")
        plt.ylabel("Feature")
        plt.title("Top XGBoost Feature Importances")
        plt.tight_layout()
        importance_path = os.path.join(output_dir, "feature_importance.png")
        plt.savefig(importance_path, dpi=150)
        plt.close()
        plot_paths["feature_importance"] = importance_path

    return plot_paths
