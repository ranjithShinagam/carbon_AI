# Technical Project Analysis: CarbonAI Platform

## 1. Executive Summary
**CarbonAI** is an industrial carbon intelligence platform designed to predict and analyze facility-level greenhouse gas (GHG) emissions ($t\text{CO}_2e$). The platform addresses the dual limitations of traditional carbon accounting (retrospective reporting, static emissions factors) and black-box machine learning (lack of domain interpretability, inability to provide operational remediation).

The system integrates:
1. An **XGBoost Regressor** trained on 18,250 multi-sector industrial records.
2. Physics-inspired, non-leaking **operational feature engineering** (energy shares, production intensities).
3. **Tree SHAP** explainability providing mathematical attribution of emission drivers.
4. A **Retrieval-Augmented Generation (RAG)** conversational advisor using FAISS dense vector search and Gemini LLM with function calling for counterfactual "what-if" simulations.
5. A **FastAPI** backend and **React** frontend supporting single simulations, flexible CSV batch processing, and persistent SQLite tracking.

---

## 2. Codebase and Architecture Inspection

### Directory Structure
```
d:\CarbonAI_3\
├── backend\
│   ├── carbon_emission_dataset_with_Industry.csv  # Primary training dataset (18,250 rows)
│   ├── database.py                                 # SQLite engine & session management
│   ├── dataset_adapter.py                          # Fuzzy CSV column matching & schema adaptation
│   ├── feature_engineering.py                      # Post-prediction operational calculations
│   ├── feature_importance.csv                      # Baseline feature importance table
│   ├── main.py                                     # FastAPI entrypoint & REST API endpoints
│   ├── model.pkl                                   # Serialized model for backward compatibility
│   ├── model_metadata.json                         # Hyperparameters, metrics, and schema metadata
│   ├── model_service.py                            # Central inference engine & schema validator
│   ├── models.py                                   # SQLAlchemy ORM models (User, PredictionHistory, ChatMessage)
│   ├── requirements.txt                            # Python dependencies
│   ├── sector_analytics.py                         # Cross-sector statistical aggregation engine
│   ├── faiss_store\                                # FAISS vector index & ESG text chunks
│   │   ├── chunks.json
│   │   └── index.faiss
│   ├── ml\                                         # Advanced ML pipeline package
│   │   ├── artifacts\                              # Production artifacts, plots, and metadata
│   │   │   ├── actual_vs_predicted.png
│   │   │   ├── feature_importance.png
│   │   │   ├── feature_metadata.json
│   │   │   ├── model.pkl
│   │   │   ├── model_metadata.json
│   │   │   ├── preprocessor.pkl
│   │   │   ├── residual_distribution.png
│   │   │   └── xgboost_model.json
│   │   ├── evaluate.py                             # Evaluation metrics & diagnostic plotting
│   │   ├── explain.py                              # Exact Tree SHAP calculation
│   │   ├── feature_engineering.py                  # Physical ratio calculations
│   │   ├── preprocessing.py                        # Categorical encoding, split logic, leakage exclusion
│   │   └── train.py                                # Master training, validation & ablation pipeline
│   └── routers\
│       ├── auth.py                                 # JWT authentication & bcrypt password hashing
│       └── chatbot.py                              # RAG document indexing & streaming LLM chat
├── frontend\
│   ├── src\
│   │   ├── api\api.js                              # REST & streaming fetch clients
│   │   ├── components\                             # UI components (sliders, gauges, batch tables, chat)
│   │   ├── context\                                # React Context (Auth, Prediction)
│   │   └── pages\                                  # Dashboard, Insights, Sector Analysis, Auth
│   ├── package.json
│   └── vite.config.js
└── sample_batch.csv                                # Sample CSV for batch prediction testing
```

---

## 3. Dataset Characteristics & Integrity Verification

- **Primary Dataset**: `carbon_emission_dataset_with_Industry.csv`
- **Total Records**: 18,250 instances
- **Features Analyzed**: 22 total columns
- **Data Completeness**: 0 missing or null values across all 18,250 rows.
- **Target Variable**: `Carbon_Emission_tCO2e_TARGET`
  - Mean: $31.84\text{ tCO}_2\text{e}$
  - Standard Deviation: $14.47\text{ tCO}_2\text{e}$
  - Minimum: $0.00\text{ tCO}_2\text{e}$
  - Median: $30.82\text{ tCO}_2\text{e}$
  - Maximum: $86.57\text{ tCO}_2\text{e}$
- **Industrial Sectors Represented**:
  - Manufacturing: 5,110 facilities (28.0%)
  - Agriculture: 4,380 facilities (24.0%)
  - Energy: 3,650 facilities (20.0%)
  - Transport: 3,650 facilities (20.0%)
  - IT / Data Centers: 1,460 facilities (8.0%)
- **Sub-Industry Sectors**:
  - Steel Manufacturing: 4,563
  - Cement Production: 4,563
  - Automotive Industry: 4,562
  - Logistics: 4,562
- **Supply Chain Transport Modes**:
  - Ship: 4,581
  - Air: 4,567
  - Truck: 4,559
  - Rail: 4,543

### Strict Data Leakage Prevention
To guarantee that the machine learning model learns true physical and operational relationships rather than trivial mathematical artifacts, 11 columns are explicitly excluded during training:
1. `Carbon_Tax_USD`: Excluded because it is mathematically derived from the target ($y \times \text{tax rate}$).
2. `Carbon_Reduction_Strategy`: Post-prediction management decision.
3. `Strategy_Implementation_Cost_USD`: Future capital expenditure (CapEx) for mitigation.
4. `Expected_Carbon_Reduction_Percent`: Prospective target goal.
5. `Expected_Renewable_Share_Percent`: Prospective renewable target.
6. `Energy_Cost_USD`: Financial billing metric rather than physical operational driver.
7. `Public_Acceptance_Index`: External ESG sentiment metric.
8. `Social_Impact_Score`: External governance rating.
9. `Process_Efficiency_Percent`: Secondary operational efficiency metric.
10. `Company_ID`: Arbitrary identifier.
11. `Date`: Timestamp used for time-series aggregation, excluded from static tabular features.

---

## 4. Machine Learning & Feature Engineering Pipeline

### A. Non-Leaking Physical Feature Engineering
From the 7 raw operational inputs ($E_{\text{total}}$, $E_{\text{ren}}$, $E_{\text{nonren}}$, $P$, $D_{\text{trans}}$, $M_{\text{raw}}$, $L$), 7 physical ratio features are constructed with safe division guarantees:
1. **Renewable Energy Share ($S_{\text{ren}}$)**: $\frac{E_{\text{ren}}}{\max(E_{\text{total}}, 1.0)} \in [0, 1]$
2. **Non-Renewable Energy Share ($S_{\text{nonren}}$)**: $\frac{E_{\text{nonren}}}{\max(E_{\text{total}}, 1.0)} \in [0, 1]$
3. **Energy per Unit Production ($I_E$)**: $\frac{E_{\text{total}}}{\max(P, 1.0)}$ (kWh / unit)
4. **Non-Renewable Energy per Unit Production ($I_{\text{NRE}}$)**: $\frac{E_{\text{nonren}}}{\max(P, 1.0)}$ (kWh / unit)
5. **Supply Chain Transport Intensity ($I_{\text{trans}}$)**: $\frac{D_{\text{trans}}}{\max(P, 1.0)}$ (km / unit)
6. **Raw Material Intensity ($I_{\text{mat}}$)**: $\frac{M_{\text{raw}}}{\max(P, 1.0)}$ (kg / unit)
7. **Energy per Employee ($I_{\text{emp}}$)**: $\frac{E_{\text{total}}}{\max(L, 1.0)}$ (kWh / employee)

### B. Preprocessing & Categorical Encoding
- Categorical features (`Sector`, `Industry_Sectors`, `Supply_Chain_Transport_Mode`) are one-hot encoded into 13 binary features.
- Final feature space: 7 raw numeric + 7 engineered physical + 13 one-hot = **27 total input features**.

### C. Hyperparameters & Optimization
- Algorithm: `xgboost.XGBRegressor`
- `n_estimators`: 350
- `max_depth`: 6
- `learning_rate`: 0.04
- `subsample`: 0.85
- `colsample_bytree`: 0.85
- `min_child_weight`: 3
- `reg_alpha` ($L_1$): 0.1
- `reg_lambda` ($L_2$): 3.0
- Optimization Objective: Mean Squared Error with second-order gradient boosting.

---

## 5. Verified Experimental Metrics

### Partitioning
- **Training Set (70%)**: 12,775 samples
- **Validation Set (15%)**: 2,737 samples
- **Untouched Holdout Test Set (15%)**: 2,738 samples

### Holdout Test Set Performance
| Evaluation Metric | Test Set Value | Validation Set Value | Unit |
| :--- | :--- | :--- | :--- |
| **Coefficient of Determination ($R^2$)** | **0.8682** | **0.8746** | Dimensionless |
| **Mean Absolute Error (MAE)** | **4.1586** | **4.0766** | $\text{tCO}_2\text{e}$ |
| **Root Mean Squared Error (RMSE)** | **5.2504** | **5.1381** | $\text{tCO}_2\text{e}$ |
| **Mean Squared Error (MSE)** | **27.5663** | **26.3998** | $(\text{tCO}_2\text{e})^2$ |
| **Median Absolute Error** | **3.3996** | **3.4465** | $\text{tCO}_2\text{e}$ |
| **Mean Absolute Percentage Error (MAPE)**| **13.16%** | **13.21%** | % |
| **Mean Residual (Bias)** | **-0.0689** | **-0.1005** | $\text{tCO}_2\text{e}$ |
| **Residual Standard Deviation** | **5.2499** | **5.1371** | $\text{tCO}_2\text{e}$ |

### Ablation Study
| Model Configuration | Features Included | Validation MAE | Validation RMSE | Validation $R^2$ |
| :--- | :--- | :--- | :--- | :--- |
| **Model A** | Base Numeric + Engineered Ratios (No Sector) | 4.1073 | 5.1511 | 0.8739 |
| **Model B** | Model A + One-Hot Sector | 4.0908 | 5.1472 | 0.8741 |
| **Model C** | Model B + Industry Sectors + Transport Modes | 4.0962 | 5.1479 | 0.8741 |
| **Final Tuned Model** | Model C with Tuned Hyperparameters (350 trees, lr=0.04) | **4.0766** | **5.1381** | **0.8746** |

### Top 10 Features by Exact Tree SHAP Attribution
| Rank | Feature Name | Mean Absolute SHAP ($t\text{CO}_2e$) | Primary Impact |
| :--- | :--- | :--- | :--- |
| 1 | `NonRenewable_Energy_Consumption_kWh` | **9.4825** | Strongly increases emissions |
| 2 | `Total_Energy_Consumption_kWh` | **0.6341** | Increases emissions scale |
| 3 | `Renewable_Energy_Share` | **0.2966** | Strongly mitigates emissions |
| 4 | `NRE_Per_Production` | **0.1552** | High intensity amplifies footprint |
| 5 | `Energy_Per_Employee` | **0.1529** | Operational scale driver |
| 6 | `Employment_Count` | **0.1443** | Facility capacity proxy |
| 7 | `Supply_Chain_Transport_km` | **0.1339** | Scope 3 logistics footprint |
| 8 | `NonRenewable_Energy_Share` | **0.1248** | Fossil reliance indicator |
| 9 | `Raw_Material_Usage_kg` | **0.1212** | Embodied Scope 3 material emissions |
| 10 | `Production_Output_Units` | **0.1156** | Manufacturing throughput denominator |

---

## 6. Conversational Advisory & RAG Pipeline

The platform pairs the predictive model with a Retrieval-Augmented Generation (RAG) advisor:
1. **Document Ingestion**: Corporate sustainability guidelines, internal carbon tax thresholds, and ESG decarbonization roadmaps (PDF or TXT) are uploaded by users.
2. **Chunking & Embeddings**: Documents are split into 600-character windows (stride 500) and embedded via `all-MiniLM-L6-v2` into 384-dimensional dense vectors.
3. **FAISS Indexing**: Embeddings are stored in a FAISS `IndexFlatIP` index using normalized inner product (cosine similarity).
4. **Bidirectional Tool Use (Gemini LLM)**:
   - To eliminate hallucinations, the model does NOT invent carbon figures. Instead, it utilizes four registered Python functions:
     - `run_whatif_prediction`: Executes real XGBoost inference for user-suggested operational changes.
     - `get_sector_and_dataset_analytics`: Retrieves verified benchmark percentiles and averages.
     - `get_model_and_shap_insights`: Pulls test metrics ($R^2$, MAE) and top SHAP feature drivers.
     - `get_my_recent_predictions`: Recalls historical user simulation sessions from SQLite.
5. **Streaming Response**: Generated advisories stream directly to the React frontend using server-sent chunks with Markdown formatting.

---

## 7. Production System & User Experience

- **Backend Gateway**: FastAPI with Pydantic validation, CORS middleware, JWT auth, and bcrypt hashing.
- **Flexible Batch Processing**: `dataset_adapter.py` enables users to upload CSVs with non-standard column headers (e.g. `Electricity` instead of `Total_Energy_Consumption_kWh`) using alias dictionaries and SequenceMatcher fuzzy resolution.
- **Frontend User Interface**:
  - Operational Sliders for instant What-If simulations.
  - Interactive SVG Emission Gauge indicating emission intensity categories.
  - Batch results table with dynamic CSV download.
  - Sector Analytics dashboard showing radar and bar comparisons across industries.
  - Expandable conversational advisor drawer with file upload attachment.
