# ============================================================
# Carbon AI - FastAPI Backend
# ============================================================
# Main API server for:
#
# - Authentication
# - Single prediction
# - Dataset upload
# - Batch prediction
# - Prediction history
# - Sector analytics
# - Dataset analytics
# - Model insights
# - Gemini AI advisor
#
# ============================================================

import os
import io
import traceback
from typing import Optional, Any

import numpy as np
import pandas as pd

from dotenv import load_dotenv

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Depends,
    HTTPException,
)
from fastapi.middleware.cors import CORSMiddleware

from pydantic import (
    BaseModel,
    Field,
    model_validator,
)

from google import genai
from google.genai import types

from sqlalchemy.orm import Session

# ============================================================
# LOCAL IMPORTS
# ============================================================

from database import Base, engine, get_db
from models import User, PredictionHistory, ChatMessage

from routers.auth import (
    router as auth_router,
    get_current_user,
    get_current_user_optional,
)

from model_service import model_service

from dataset_adapter import (
    adapt_dataset,
)

from sector_analytics import (
    calculate_all_analytics,
)


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

from routers.chatbot import router as chatbot_router

# ============================================================
# GEMINI CONFIGURATION
# ============================================================
GOOGLE_API_KEY = os.getenv(
    "GOOGLE_API_KEY"
)

if GOOGLE_API_KEY:
    try:
        GEMINI_CLIENT = genai.Client(
            api_key=GOOGLE_API_KEY,
            http_options=types.HttpOptions(
                retry_options=types.HttpRetryOptions(attempts=1)
            ),
        )

        GEMINI_MODEL = "gemini-3.6-flash"
        GEMINI_FALLBACK_MODELS = [
            "gemini-3.6-flash",
            "gemini-3.5-flash",
            "gemini-3.7-flash",
            "gemini-3.5-flash-lite",
            "gemini-3.1-flash-lite",
            "gemini-3.8-flash",
        ]

    except Exception:
        GEMINI_CLIENT = None
        GEMINI_MODEL = None
        GEMINI_FALLBACK_MODELS = []

else:
    GEMINI_CLIENT = None
    GEMINI_MODEL = None
    GEMINI_FALLBACK_MODELS = []

# ============================================================
# DATABASE INITIALIZATION
# ============================================================

Base.metadata.create_all(
    bind=engine
)

from sqlalchemy import text
with engine.begin() as conn:
    existing_cols = {row[1] for row in conn.execute(text("PRAGMA table_info(prediction_history)"))}
    for col_name in ("sector", "industry_sector", "transport_mode"):
        if col_name not in existing_cols:
            conn.execute(text(f"ALTER TABLE prediction_history ADD COLUMN {col_name} VARCHAR"))


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="Carbon AI API",
    description=(
        "Carbon emission prediction, "
        "analytics and AI advisory API."
    ),
    version="2.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# ROUTERS
# ============================================================

app.include_router(
    auth_router
)

app.include_router(
    chatbot_router
)


# ============================================================
# JSON SERIALIZATION HELPER
# ============================================================

def make_json_safe(
    value: Any
):
    """
    Recursively convert NumPy/Pandas values
    into native Python JSON-compatible values.

    Fixes errors such as:

        TypeError:
        'numpy.bool_' object is not iterable
    """

    # --------------------------------------------------------
    # Dictionary
    # --------------------------------------------------------

    if isinstance(
        value,
        dict
    ):
        return {
            str(key): make_json_safe(
                val
            )
            for key, val in value.items()
        }

    # --------------------------------------------------------
    # List / Tuple
    # --------------------------------------------------------

    if isinstance(
        value,
        (list, tuple)
    ):
        return [
            make_json_safe(
                item
            )
            for item in value
        ]

    # --------------------------------------------------------
    # NumPy boolean
    # --------------------------------------------------------

    if isinstance(
        value,
        np.bool_
    ):
        return bool(value)

    # --------------------------------------------------------
    # NumPy integer
    # --------------------------------------------------------

    if isinstance(
        value,
        np.integer
    ):
        return int(value)

    # --------------------------------------------------------
    # NumPy floating point
    # --------------------------------------------------------

    if isinstance(
        value,
        np.floating
    ):

        if (
            np.isnan(value)
            or np.isinf(value)
        ):
            return None

        return float(value)

    # --------------------------------------------------------
    # Normal Python float
    # --------------------------------------------------------

    if isinstance(
        value,
        float
    ):

        if (
            np.isnan(value)
            or np.isinf(value)
        ):
            return None

    # --------------------------------------------------------
    # Pandas NA / NaN
    # --------------------------------------------------------

    try:

        if pd.isna(value):
            return None

    except (
        TypeError,
        ValueError
    ):
        pass

    # --------------------------------------------------------
    # Already JSON-safe
    # --------------------------------------------------------

    return value


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    model_info = model_service.get_model_info()

    return {
        "message": "CARBON AI API STARTED",
        "model_loaded": model_info.get("model_loaded", False),
        "model_type": model_info.get("model_type")
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():
    model_info = model_service.get_model_info()

    return {
        "status": "ok",
        "model_loaded": model_info.get("model_loaded", False),
        "model_type": model_info.get("model_type"),
    }
    
@app.get("/prediction-options")
def prediction_options():
    return make_json_safe(model_service.get_prediction_options())


# ============================================================
# PREDICTION REQUEST
# ============================================================

class PredictionRequest(
    BaseModel
):

    total_energy: float = Field(
        ...,
        ge=0
    )

    renewable_energy: float = Field(
        ...,
        ge=0
    )

    nonrenewable_energy: float = Field(
        ...,
        ge=0
    )

    production_output: float = Field(
        ...,
        ge=0
    )

    transport_distance: float = Field(
        ...,
        ge=0
    )

    raw_material_usage: float = Field(
        ...,
        ge=0
    )

    employment_count: float = Field(
        ...,
        ge=0
    )

    sector: Optional[str] = None

    industry_sector: Optional[str] = None

    transport_mode: Optional[str] = None

    # --------------------------------------------------------
    # Energy validation
    # --------------------------------------------------------

    @model_validator(
        mode="after"
    )
    def validate_energy(
        self
    ):

        renewable = (
            self.renewable_energy
        )

        nonrenewable = (
            self.nonrenewable_energy
        )

        total = (
            self.total_energy
        )

        energy_sum = (
            renewable
            + nonrenewable
        )

        # Renewable + non-renewable
        # cannot exceed total energy.

        if energy_sum > (
            total + max(
                1.0,
                total * 0.01
            )
        ):

            raise ValueError(
                "Renewable energy + "
                "non-renewable energy "
                "cannot exceed total energy."
            )

        # If total energy > 0, require
        # approximate consistency.

        if total > 0:

            difference = abs(
                energy_sum - total
            )

            tolerance = max(
                1.0,
                total * 0.01
            )

            if difference > tolerance:

                raise ValueError(
                    "Renewable energy + "
                    "non-renewable energy "
                    "must approximately equal "
                    "total energy within 1%."
                )

        return self


# ============================================================
# SINGLE PREDICTION
# ============================================================

@app.post(
    "/predict"
)
def predict(
    request: PredictionRequest,
    current_user: Optional[User] = Depends(
        get_current_user_optional
    ),
    db: Session = Depends(
        get_db
    ),
):

    try:

        # ----------------------------------------------------
        # Convert frontend request to model features
        # ----------------------------------------------------

        input_data = {

            "Total_Energy_Consumption_kWh":
                request.total_energy,

            "Renewable_Energy_Consumption_kWh":
                request.renewable_energy,

            "NonRenewable_Energy_Consumption_kWh":
                request.nonrenewable_energy,

            "Production_Output_Units":
                request.production_output,

            "Supply_Chain_Transport_km":
                request.transport_distance,

            "Raw_Material_Usage_kg":
                request.raw_material_usage,

            "Employment_Count":
                request.employment_count,
            "Sector": request.sector,
                       "Industry_Sectors": request.industry_sector,
                       "Supply_Chain_Transport_Mode": request.transport_mode,
        }

        # ----------------------------------------------------
        # XGBoost prediction
        # ----------------------------------------------------

        result = model_service.predict(
            input_data
        )

        history_id = None

        # ----------------------------------------------------
        # Save authenticated user's prediction
        # ----------------------------------------------------

        if current_user is not None:

            history = PredictionHistory(

                user_id=current_user.id,

                total_energy=
                    request.total_energy,

                renewable_energy=
                    request.renewable_energy,

                nonrenewable_energy=
                    request.nonrenewable_energy,

                production_output=
                    request.production_output,

                transport_distance=
                    request.transport_distance,

                raw_material_usage=
                    request.raw_material_usage,

                employment_count=
                    request.employment_count,

                predicted_co2_emission=
                    result[
                        "predicted_co2"
                    ],

                carbon_intensity=
                    result[
                        "carbon_intensity"
                    ],

                energy_per_employee=
                    result[
                        "energy_per_employee"
                    ],

                renewable_energy_ratio=
                    result[
                        "renewable_energy_ratio"
                    ],

                nonrenewable_energy_ratio=
                    result[
                        "nonrenewable_energy_ratio"
                    ],
                sector=request.sector,
                      industry_sector=request.industry_sector,
                       transport_mode=request.transport_mode,
            )

            db.add(
                history
            )

            db.commit()

            db.refresh(
                history
            )

            history_id = (
                history.id
            )

        # ----------------------------------------------------
        # Response
        # ----------------------------------------------------

        response = {

            "success": True,

            "prediction": result,

            "history_id":
                history_id,

            "user_id": (
                current_user.id
                if current_user is not None
                else None
            ),
        }

        return make_json_safe(
            response
        )

    except HTTPException:
        raise

    except Exception as e:

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=(
                "Prediction failed: "
                f"{str(e)}"
            )
        )


# ============================================================
# UPLOAD DATASET
# ============================================================

@app.post(
    "/upload-dataset"
)
async def upload_dataset(
    file: UploadFile = File(...),
    current_user: Optional[User] = Depends(
        get_current_user_optional
    ),
):

    try:

        # ====================================================
        # 1. VALIDATE FILE
        # ====================================================

        if not file.filename:

            raise HTTPException(
                status_code=400,
                detail="No file selected."
            )

        if not file.filename.lower().endswith(
            ".csv"
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    "Only CSV files are supported."
                )
            )

        # ====================================================
        # 2. READ CSV
        # ====================================================

        contents = await file.read()

        if not contents:

            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty."
            )

        try:

            df = pd.read_csv(
                io.BytesIO(
                    contents
                )
            )

        except Exception as e:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Unable to read CSV file: "
                    f"{str(e)}"
                )
            )

        if df.empty:

            raise HTTPException(
                status_code=400,
                detail="CSV contains no rows."
            )

        print(
            "\n" + "=" * 70
        )

        print(
            "CARBON AI - DATASET UPLOAD"
        )

        print(
            "=" * 70
        )

        print(
            f"Filename: {file.filename}"
        )

        print(
            f"Original shape: {df.shape}"
        )

        print(
            "Original columns:"
        )

        print(
            df.columns.tolist()
        )

        # ====================================================
        # 3. DATASET ADAPTER
        # ====================================================

        adapted = adapt_dataset(
            df
        )

        # ----------------------------------------------------
        # Validate adapter response
        # ----------------------------------------------------

        if not isinstance(
            adapted,
            dict
        ):

            raise HTTPException(
                status_code=500,
                detail=(
                    "Dataset adapter returned "
                    "an unexpected result."
                )
            )

        # ====================================================
        # 4. CHECK ADAPTER SUCCESS
        # ====================================================

        if not adapted.get(
            "success",
            False
        ):

            raise HTTPException(
                status_code=400,
                detail=make_json_safe({

                    "message":
                        "Dataset validation failed.",

                    "errors":
                        adapted.get(
                            "errors",
                            []
                        ),

                    "warnings":
                        adapted.get(
                            "warnings",
                            []
                        ),

                    "mapping":
                        adapted.get(
                            "mapping",
                            {}
                        ),

                })
            )

        # ====================================================
        # 5. GET PROCESSED DATAFRAME
        # ====================================================

        processed_df = adapted.get(
            "data"
        )

        if processed_df is None:

            raise HTTPException(
                status_code=500,
                detail=(
                    "Dataset adapter did not "
                    "return processed data."
                )
            )

        if not isinstance(
            processed_df,
            pd.DataFrame
        ):

            raise HTTPException(
                status_code=500,
                detail=(
                    "Dataset adapter returned "
                    "an invalid dataframe."
                )
            )

        if processed_df.empty:

            raise HTTPException(
                status_code=400,
                detail=(
                    "No valid rows remain after "
                    "dataset processing."
                )
            )

        print(
            f"Processed shape: "
            f"{processed_df.shape}"
        )

        print(
            "Processed columns:"
        )

        print(
            processed_df.columns.tolist()
        )

        # ====================================================
        # 6. XGBOOST BATCH PREDICTION
        # ====================================================

        prediction_df = (
            model_service.predict_dataframe(
                processed_df.copy()
            )
        )

        if prediction_df is None:

            raise HTTPException(
                status_code=500,
                detail=(
                    "Model prediction returned "
                    "no data."
                )
            )

        if prediction_df.empty:

            raise HTTPException(
                status_code=500,
                detail=(
                    "Model produced an empty "
                    "prediction dataset."
                )
            )

        print(
            f"Prediction shape: "
            f"{prediction_df.shape}"
        )

        print(
            "Prediction columns:"
        )

        print(
            prediction_df.columns.tolist()
        )

        # ====================================================
        # 7. SECTOR / INDUSTRY ANALYTICS
        # ====================================================

        analytics = (
            calculate_all_analytics(
                prediction_df
            )
        )

        print(
            "Sector/industry analytics generated."
        )

        # ====================================================
        # 8. PREDICTION SUMMARY
        # ====================================================

        prediction_column = (
            "Predicted_Carbon_Emission_tCO2e"
        )

        if prediction_column not in (
            prediction_df.columns
        ):

            raise HTTPException(
                status_code=500,
                detail=(
                    "Prediction column was not "
                    "generated by model service."
                )
            )

        prediction_values = pd.to_numeric(
            prediction_df[
                prediction_column
            ],
            errors="coerce"
        )

        prediction_values = (
            prediction_values
            .replace(
                [np.inf, -np.inf],
                np.nan
            )
            .dropna()
        )

        if prediction_values.empty:

            raise HTTPException(
                status_code=500,
                detail=(
                    "Model predictions contain "
                    "no valid numeric values."
                )
            )

        prediction_summary = {

            "records":
                int(
                    len(prediction_df)
                ),

            "average_predicted_co2":
                float(
                    prediction_values.mean()
                ),

            "total_predicted_co2":
                float(
                    prediction_values.sum()
                ),

            "minimum_predicted_co2":
                float(
                    prediction_values.min()
                ),

            "maximum_predicted_co2":
                float(
                    prediction_values.max()
                ),
        }

        # ====================================================
        # 9. BUILD RESPONSE
        # ====================================================

        response = {

            "success": True,

            "filename":
                file.filename,

            "metadata": {

                "original_rows":
                    int(
                        adapted.get(
                            "original_rows",
                            len(df)
                        )
                    ),

                "final_rows":
                    int(
                        len(processed_df)
                    ),

                "columns":
                    int(
                        len(
                            processed_df.columns
                        )
                    ),
            },

            "mapping":
                adapted.get(
                    "mapping",
                    {}
                ),

            "ignored_columns":
                adapted.get(
                    "ignored_columns",
                    []
                ),

            "warnings":
                adapted.get(
                    "warnings",
                    []
                ),

            "errors":
                adapted.get(
                    "errors",
                    []
                ),

            "energy_validation":
                adapted.get(
                    "energy_validation",
                    {}
                ),

            "duplicates_removed":
                adapted.get(
                    "duplicates_removed",
                    0
                ),

            "prediction_summary":
                prediction_summary,

            "sector_analytics":
                analytics,

            "user_id": (

                int(
                    current_user.id
                )

                if current_user is not None

                else None
            ),
        }

        # ====================================================
        # 10. IMPORTANT
        # Convert all NumPy/Pandas values
        # before FastAPI serialization.
        # ====================================================

        safe_response = (
            make_json_safe(
                response
            )
        )

        print(
            "\nDataset upload completed successfully."
        )

        print(
            "=" * 70
        )

        return safe_response

    # ========================================================
    # PRESERVE HTTP ERRORS
    # ========================================================

    except HTTPException:
        raise

    # ========================================================
    # UNEXPECTED ERROR
    # ========================================================

    except Exception as e:

        print(
            "\n" + "=" * 70
        )

        print(
            "CARBON AI - DATASET UPLOAD ERROR"
        )

        print(
            "=" * 70
        )

        traceback.print_exc()

        print(
            "=" * 70
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Dataset processing failed: "
                f"{str(e)}"
            )
        )


# ============================================================
# BATCH PREDICTION
# ============================================================

@app.post(
    "/predict/batch"
)
async def predict_batch(
    file: UploadFile = File(...),
    current_user: Optional[User] = Depends(
        get_current_user_optional
    ),
):

    return await upload_dataset(
        file=file,
        current_user=current_user
    )


# ============================================================
# USER PREDICTION HISTORY
# ============================================================

@app.get(
    "/history"
)
def get_history(
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_db
    ),
):

    try:

        records = (
            db.query(
                PredictionHistory
            )
            .filter(
                PredictionHistory.user_id
                == current_user.id
            )
            .order_by(
                PredictionHistory.created_at.desc()
            )
            .all()
        )

        result = []

        for item in records:

            result.append({

                "id":
                    item.id,

                "user_id":
                    item.user_id,

                "total_energy":
                    item.total_energy,

                "renewable_energy":
                    item.renewable_energy,

                "nonrenewable_energy":
                    item.nonrenewable_energy,

                "production_output":
                    item.production_output,

                "transport_distance":
                    item.transport_distance,

                "raw_material_usage":
                    item.raw_material_usage,

                "employment_count":
                    item.employment_count,

                "predicted_co2_emission":
                    item.predicted_co2_emission,

                "carbon_intensity":
                    item.carbon_intensity,

                "energy_per_employee":
                    item.energy_per_employee,

                "renewable_energy_ratio":
                    item.renewable_energy_ratio,

                "nonrenewable_energy_ratio":
                    item.nonrenewable_energy_ratio,

                "created_at":
                    item.created_at,
                "sector": item.sector,
                         "industry_sector": item.industry_sector,
                         "transport_mode": item.transport_mode,
            })

        return make_json_safe(
            result
        )

    except Exception as e:

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to retrieve history: "
                f"{str(e)}"
            )
        )


# ============================================================
# LOAD ORIGINAL DATASET
# ============================================================

def load_carbon_dataset():

    dataset_path = os.path.join(
        os.path.dirname(
            os.path.abspath(__file__)
        ),
        "carbon_emission_dataset_with_Industry.csv"
    )

    if not os.path.exists(
        dataset_path
    ):

        raise FileNotFoundError(
            "carbon_emission_dataset_with_Industry.csv "
            "was not found in the backend directory."
        )

    return pd.read_csv(
        dataset_path
    )


# ============================================================
# SECTOR INSIGHTS
# ============================================================

@app.get(
    "/sector-insights"
)
def sector_insights():

    try:

        df = load_carbon_dataset()

        analytics = (
            calculate_all_analytics(
                df
            )
        )

        return make_json_safe(
            analytics
        )

    except Exception as e:

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to generate sector "
                f"insights: {str(e)}"
            )
        )


# ============================================================
# MODEL INSIGHTS
# ============================================================

@app.get(
    "/model-insights"
)
def model_insights():

    try:

        model_info = (
            model_service.get_model_info()
        )

        feature_importance = (
            model_service.get_feature_importance()
        )

        return make_json_safe({

            "success": True,

            "model": model_info,

            "feature_importance":
                feature_importance,
        })

    except Exception as e:

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to retrieve model "
                f"insights: {str(e)}"
            )
        )


# ============================================================
# DATASET INSIGHTS
# ============================================================

@app.get(
    "/dataset-insights"
)
def dataset_insights():

    try:

        df = load_carbon_dataset()

        analytics = (
            calculate_all_analytics(
                df
            )
        )

        return make_json_safe({

            "success": True,

            "analytics":
                analytics,

        })

    except Exception as e:

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to generate dataset "
                f"insights: {str(e)}"
            )
        )


# ============================================================
# GEMINI AI ADVISOR
# ============================================================

class AIRequest(
    BaseModel
):

    message: str

    prediction: Optional[dict] = None


# ============================================================
# AI ADVISOR ENDPOINT
# ============================================================

@app.post(
    "/ask-ai"
)
def ask_ai(
    request: AIRequest
):

    # --------------------------------------------------------
    # Gemini not configured
    # --------------------------------------------------------

    if GEMINI_MODEL is None:

        raise HTTPException(
            status_code=503,
            detail=(
                "Gemini AI is not configured. "
                "Set GOOGLE_API_KEY in the environment."
            )
        )

    try:

        # ----------------------------------------------------
        # Load real dataset analytics
        # ----------------------------------------------------

        df = load_carbon_dataset()

        analytics = (
            calculate_all_analytics(
                df
            )
        )

        overall = analytics.get(
            "overall",
            {}
        )

        sectors = analytics.get(
            "sectors",
            []
        )

        industries = analytics.get(
            "industries",
            []
        )

        # ----------------------------------------------------
        # Get real model information
        # ----------------------------------------------------

        model_info = (
            model_service.get_model_info()
        )

        feature_importance = (
            model_service.get_feature_importance()
        )

        # ----------------------------------------------------
        # Current user prediction
        # ----------------------------------------------------

        current_prediction = (
            request.prediction
            if request.prediction
            else None
        )

        # ----------------------------------------------------
        # Build real Carbon AI context
        # ----------------------------------------------------

        context = {

            "current_prediction":
                current_prediction,

            "overall_dataset_analytics":
                overall,

            "sector_analytics":
                sectors,

            "industry_analytics":
                industries,

            "model_information":
                model_info,

            "feature_importance":
                feature_importance,
        }

        # ----------------------------------------------------
        # Gemini prompt
        # ----------------------------------------------------

        prompt = f"""
You are Carbon AI Advisor.

You are an AI sustainability assistant inside
a carbon-emission prediction application.

Your job is to explain the application's
REAL carbon analytics and provide practical
sustainability guidance.

IMPORTANT RULES:

1. The XGBoost model is responsible for
   numerical carbon-emission predictions.

2. Never invent or calculate an alternative
   carbon-emission prediction.

3. If a current prediction is provided below,
   use that exact prediction when discussing
   the user's current result.

4. Do not change, estimate, or replace the
   XGBoost prediction.

5. Use the supplied dataset analytics when
   discussing sector, industry, energy,
   production, employment, or carbon trends.

6. Clearly distinguish:
   - the user's current prediction
   - dataset observations
   - general sustainability recommendations.

7. Do not invent company-specific information.

8. If the user asks why their prediction is high
   or low, use the supplied feature importance
   information and the user's available metrics.

9. If the user asks how to reduce emissions,
   provide practical recommendations based on
   the available operational metrics.

10. Do not claim that a recommendation will
    reduce emissions by a specific percentage
    unless that percentage is explicitly present
    in the supplied context.

11. Keep numerical answers grounded in the
    supplied data.

12. Do not pretend that Gemini itself is the
    prediction model.

REAL CARBON AI CONTEXT:

{context}

USER QUESTION:

{request.message}

Answer clearly and concisely.

When relevant, structure your response using:

- Current result
- What it means
- Key drivers
- Recommended actions

Do not mention internal implementation details
unless the user asks about the technology.
"""

        # ----------------------------------------------------
        # Generate Gemini response
        # ----------------------------------------------------

       
       
        answer = None
        last_err = None
        for model_name in GEMINI_FALLBACK_MODELS:
            try:
                response = GEMINI_CLIENT.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                answer = response.text
                break
            except Exception as model_err:
                last_err = model_err
                err_str = str(model_err)
                if any(code in err_str for code in ("503", "429", "404", "UNAVAILABLE", "RESOURCE_EXHAUSTED")):
                    continue
                raise

        if answer is None and last_err is not None:
            raise last_err

        if not answer:

            answer = (
                "I could not generate an AI response "
                "at this time."
            )

        return {

            "success": True,

            "answer": answer,

        }

    except Exception as e:

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=(
                "AI advisor failed: "
                f"{str(e)}"
            )
        )



# ============================================================
# APPLICATION STARTUP
# ============================================================

@app.on_event("startup")
async def startup_event():

    print(
        "\n" + "=" * 70
    )

    print(
        "CARBON AI API STARTED"
    )

    print(
        "=" * 70
    )

    model_info = (
        model_service.get_model_info()
    )

    print(
        "Model information:",
        model_info
    )

    print(
        "Gemini configured:",
        GEMINI_MODEL is not None
    )

    print(
        "=" * 70
    )