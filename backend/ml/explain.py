"""
SHAP Explainability Module for CarbonAI XGBoost Model.
Provides both global feature attribution and local sample-level explanations.
"""

from typing import Dict, Any, List, Optional, Union
import numpy as np
import pandas as pd
import xgboost as xgb


class CarbonShapExplainer:
    """
    Computes exact Tree SHAP values using XGBoost Tree SHAP and optional shap library.
    """
    def __init__(self, model: Any, feature_names: List[str], base_value: Optional[float] = None):
        self.model = model
        self.feature_names = feature_names
        self._booster = model.get_booster() if hasattr(model, "get_booster") else model
        self.base_value = base_value

        # Attempt to initialize shap.TreeExplainer if shap library is present
        self.shap_explainer = None
        try:
            import shap
            self.shap_explainer = shap.TreeExplainer(self.model)
            if self.base_value is None and hasattr(self.shap_explainer, "expected_value"):
                ev = self.shap_explainer.expected_value
                self.base_value = float(ev if np.isscalar(ev) else ev[0])
        except Exception:
            self.shap_explainer = None

    def explain_local(self, X_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Computes local SHAP breakdown for each sample in X_df.
        
        Returns a list of records containing:
            - predicted_emission
            - base_value
            - feature_contributions: list of {feature, value, shap_value, direction}
        """
        # Ensure correct column ordering
        X_ordered = X_df[self.feature_names].copy()
        dmatrix = xgb.DMatrix(X_ordered)

        # Exact Tree SHAP contributions from XGBoost: shape (n_samples, n_features + 1)
        # Last column is the bias / base value phi_0
        contribs = self._booster.predict(dmatrix, pred_contribs=True)
        
        results = []
        for i in range(len(X_ordered)):
            row_contribs = contribs[i]
            feature_shap = row_contribs[:-1]
            bias = float(row_contribs[-1])
            base_val = self.base_value if self.base_value is not None else bias
            pred_val = float(np.sum(row_contribs))

            contributions = []
            for feat_name, shap_val, feat_val in zip(self.feature_names, feature_shap, X_ordered.iloc[i]):
                direction = "Increases predicted emissions" if shap_val > 0 else "Reduces predicted emissions"
                contributions.append({
                    "feature": feat_name,
                    "value": float(feat_val) if isinstance(feat_val, (int, float, np.number)) else str(feat_val),
                    "shap_value": round(float(shap_val), 4),
                    "impact_magnitude": round(abs(float(shap_val)), 4),
                    "direction": direction
                })

            # Sort contributions by absolute impact
            contributions.sort(key=lambda x: x["impact_magnitude"], reverse=True)

            results.append({
                "predicted_emission": round(pred_val, 4),
                "base_value": round(base_val, 4),
                "feature_contributions": contributions
            })

        return results

    def explain_global(self, X_sample: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Computes global mean |SHAP| values across a representative sample.
        """
        X_ordered = X_sample[self.feature_names].copy()
        dmatrix = xgb.DMatrix(X_ordered)
        contribs = self._booster.predict(dmatrix, pred_contribs=True)[:, :-1]
        mean_abs_shap = np.mean(np.abs(contribs), axis=0)

        ranking = []
        for feat_name, mean_shap in zip(self.feature_names, mean_abs_shap):
            ranking.append({
                "feature": feat_name,
                "mean_abs_shap": round(float(mean_shap), 4)
            })

        ranking.sort(key=lambda x: x["mean_abs_shap"], reverse=True)
        return ranking
