# ============================================
# XGBoost Carbon Emission Prediction Model
# ============================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import os

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from xgboost import XGBRegressor

# ============================================
# 1 Load Dataset
# ============================================
dataset_path = "trail_df.csv"
if not os.path.exists(dataset_path):
    print(f"Error: Dataset not found at {dataset_path}")
    print("Please make sure the dataset is in the backend/ directory before training.")
    exit(1)

df = pd.read_csv(dataset_path)

print("\nDataset Shape:")
print(df.shape)
print("\nFirst Rows:")
print(df.head())

# ============================================
# 2 Feature Engineering
# ============================================

# ============================================
# 3 Feature Selection
# ============================================
features = [
    "Electricity",
    "NRE_consumption",
    "Production",
    "transport_km",
    "raw_material",
    "emp_count",
]

X = df[features]
y = df["target"]

# ============================================
# 4 Train Test Split
# ============================================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ============================================
# 5 Hyperparameter Tuning
# ============================================
param_grid = {
    "n_estimators": [200, 300],
    "max_depth": [4, 6, 8],
    "learning_rate": [0.01, 0.05, 0.1],
    "subsample": [0.8, 1],
    "colsample_bytree": [0.8, 1]
}

xgb = XGBRegressor(random_state=42)

grid = GridSearchCV(
    estimator=xgb,
    param_grid=param_grid,
    cv=3,
    scoring="r2",
    n_jobs=-1
)

print("\nRunning Hyperparameter Tuning...")
grid.fit(X_train, y_train)

best_model = grid.best_estimator_

print("\nBest Parameters:")
print(grid.best_params_)

# ============================================
# 6 Train Final Model
# ============================================
best_model.fit(X_train, y_train)
predictions = best_model.predict(X_test)

# ============================================
# 7 Model Evaluation
# ============================================
r2 = r2_score(y_test, predictions)
mae = mean_absolute_error(y_test, predictions)
rmse = np.sqrt(mean_squared_error(y_test, predictions))

print("\nModel Performance")
print("R2 Score:", r2)
print("MAE:", mae)
print("RMSE:", rmse)

# ============================================
# 8 Save Model
# ============================================
model_file = "model.pkl"
joblib.dump(best_model, model_file)
print(f"\nModel saved successfully as {model_file}")

# Note: The visual plots have been omitted for automated execution, 
# but they remain available in the user's provided script.
