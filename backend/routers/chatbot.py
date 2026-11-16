import os
import io
import json
import threading
import traceback
from functools import lru_cache
from typing import Optional

import faiss
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from google import genai
from google.genai import types
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader

from database import SessionLocal, get_db
from models import ChatMessage, PredictionHistory, User
from routers.auth import get_current_user_optional
from model_service import model_service
from sector_analytics import calculate_all_analytics

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BACKEND_DIR, ".env"))

router = APIRouter(prefix="/api/chat", tags=["Chatbot"])

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
FALLBACK_MODELS = [
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.7-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3.8-flash",
]
client = (
    genai.Client(
        api_key=GOOGLE_API_KEY,
        http_options=types.HttpOptions(
            retry_options=types.HttpRetryOptions(attempts=1)
        ),
    )
    if GOOGLE_API_KEY
    else None
)

FAISS_DIR = os.path.join(BACKEND_DIR, "faiss_store")
FAISS_INDEX_PATH = os.path.join(FAISS_DIR, "index.faiss")
FAISS_CHUNKS_PATH = os.path.join(FAISS_DIR, "chunks.json")
EMBED_DIM = 384

_embed_model: Optional[SentenceTransformer] = None
_faiss_index: Optional[faiss.IndexFlatIP] = None
_faiss_chunks: list[dict] = []
_rag_lock = threading.Lock()


def get_embed_model() -> SentenceTransformer:
    global _embed_model
    if _embed_model is None:
        _embed_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _embed_model


def _ensure_faiss_loaded():
    global _faiss_index, _faiss_chunks
    if _faiss_index is not None:
        return
    os.makedirs(FAISS_DIR, exist_ok=True)
    if os.path.exists(FAISS_INDEX_PATH) and os.path.exists(FAISS_CHUNKS_PATH):
        _faiss_index = faiss.read_index(FAISS_INDEX_PATH)
        with open(FAISS_CHUNKS_PATH, "r", encoding="utf-8") as f:
            _faiss_chunks = json.load(f)
    else:
        _faiss_index = faiss.IndexFlatIP(EMBED_DIM)
        _faiss_chunks = []


def _save_faiss_store():
    os.makedirs(FAISS_DIR, exist_ok=True)
    faiss.write_index(_faiss_index, FAISS_INDEX_PATH)
    with open(FAISS_CHUNKS_PATH, "w", encoding="utf-8") as f:
        json.dump(_faiss_chunks, f, ensure_ascii=False, indent=2)


@lru_cache(maxsize=1)
def get_cached_dataset_analytics() -> dict:
    dataset_path = os.path.join(BACKEND_DIR, "carbon_emission_dataset_with_Industry.csv")
    if not os.path.exists(dataset_path):
        return {}
    df = pd.read_csv(dataset_path)
    return calculate_all_analytics(df)


def get_training_artifacts_summary() -> dict:
    meta_path = os.path.join(BACKEND_DIR, "ml", "artifacts", "model_metadata.json")
    if not os.path.exists(meta_path):
        return {}
    with open(meta_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {
        "test_metrics": data.get("test_metrics"),
        "top_shap_features": data.get("top_shap_features"),
        "model_comparison": data.get("model_comparison"),
    }


# ---------------- RAG ENDPOINTS (FAISS) ----------------
@router.post("/upload")
async def upload_rag_document(
    file: UploadFile = File(...),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file selected.")

    content = await file.read()
    if file.filename.lower().endswith(".pdf"):
        reader = PdfReader(io.BytesIO(content))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    else:
        text = content.decode("utf-8", errors="ignore")

    text = text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="No readable text found in file.")

    chunks = [text[i:i + 600] for i in range(0, len(text), 500) if text[i:i + 600].strip()]
    vectors = get_embed_model().encode(chunks, normalize_embeddings=True)
    vectors = np.asarray(vectors, dtype="float32")
    uid = current_user.id if current_user else None

    with _rag_lock:
        _ensure_faiss_loaded()
        _faiss_index.add(vectors)
        for chunk in chunks:
            _faiss_chunks.append({"user_id": uid, "source": file.filename, "text": chunk})
        _save_faiss_store()

    return {"success": True, "filename": file.filename, "chunks_indexed": len(chunks)}


@router.get("/documents")
def list_rag_documents(current_user: Optional[User] = Depends(get_current_user_optional)):
    uid = current_user.id if current_user else None
    with _rag_lock:
        _ensure_faiss_loaded()
        sources = sorted({
            c["source"] for c in _faiss_chunks
            if c.get("user_id") in (uid, None)
        })
    return {"documents": sources}


def retrieve_rag_context(query: str, user_id: Optional[int], top_k: int = 4) -> str:
    with _rag_lock:
        _ensure_faiss_loaded()
        if _faiss_index.ntotal == 0:
            return ""

        query_lower = query.lower()
        named_matches = [
            f"[Source: {c['source']}]\n{c['text']}"
            for c in _faiss_chunks
            if c.get("user_id") in (user_id, None) and c["source"].lower() in query_lower
        ]
        if named_matches:
            return "\n---\n".join(named_matches[:top_k])

        q_vec = get_embed_model().encode([query], normalize_embeddings=True)
        q_vec = np.asarray(q_vec, dtype="float32")

        search_k = min(_faiss_index.ntotal, max(top_k * 4, 15))
        scores, indices = _faiss_index.search(q_vec, search_k)

        matched = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(_faiss_chunks):
                continue
            item = _faiss_chunks[idx]
            if item.get("user_id") not in (user_id, None):
                continue
            if score < 0.15:
                continue
            matched.append(f"[Source: {item['source']}]\n{item['text']}")
            if len(matched) >= top_k:
                break

        return "\n---\n".join(matched)


# ---------------- CHAT HISTORY ----------------
@router.get("/history/{session_id}")
def get_chat_history(
    session_id: str,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    query = db.query(ChatMessage).filter(ChatMessage.session_id == session_id)
    if current_user:
        query = query.filter(ChatMessage.user_id == current_user.id)
    msgs = query.order_by(ChatMessage.created_at.asc()).all()
    return {
        "messages": [
            {"role": m.role, "text": m.content, "created_at": m.created_at}
            for m in msgs
        ]
    }


# ---------------- STREAMING CHAT ----------------
class ChatRequest(BaseModel):
    session_id: str
    message: str
    current_prediction: Optional[dict] = None


@router.post("/stream")
def chat_stream(
    req: ChatRequest,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    if not client:
        raise HTTPException(status_code=503, detail="GOOGLE_API_KEY is not configured.")

    user_id = current_user.id if current_user else None

    prev_query = db.query(ChatMessage).filter(ChatMessage.session_id == req.session_id)
    if user_id is not None:
        prev_query = prev_query.filter(ChatMessage.user_id == user_id)
    prev_msgs = prev_query.order_by(ChatMessage.created_at.asc()).limit(20).all()

    history_contents = [
        types.Content(role=m.role, parts=[types.Part.from_text(text=m.content)])
        for m in prev_msgs
    ]

    db.add(ChatMessage(
        user_id=user_id,
        session_id=req.session_id,
        role="user",
        content=req.message,
    ))
    db.commit()

    rag_context = retrieve_rag_context(req.message, user_id=user_id)

    system_instruction = (
        "You are Carbon AI Advisor inside a carbon-emission prediction & analytics dashboard.\n"
        "Rules:\n"
        "1. NEVER invent or estimate CO2 predictions yourself. Always call `run_whatif_prediction` or cite `current_prediction`.\n"
        "2. Use tools when asked about sector/industry trends, XGBoost R2/MAE/SHAP drivers, or saved prediction history.\n"
        "3. Ground document answers in the Uploaded Document Context when provided.\n"
    )
    if req.current_prediction:
        system_instruction += f"\nActive Dashboard Prediction:\n{json.dumps(req.current_prediction, default=str)}\n"
    if rag_context:
        system_instruction += f"\nUploaded Document Context (RAG):\n{rag_context}\n"

    contents = history_contents + [
        types.Content(role="user", parts=[types.Part.from_text(text=req.message)])
    ]

    # --- Tools ---
    def get_sector_and_dataset_analytics() -> dict:
        """Fetch overall dataset statistics, sector breakdown, and industry emission analytics."""
        return get_cached_dataset_analytics()

    def get_model_and_shap_insights() -> dict:
        """Fetch XGBoost model info, test metrics (R2, MAE, RMSE), feature importance, and global SHAP values."""
        return {
            "model_info": model_service.get_model_info(),
            "feature_importance": model_service.get_feature_importance(),
            "training_evaluation": get_training_artifacts_summary(),
        }

    def run_whatif_prediction(
        total_energy: float,
        renewable_energy: float,
        nonrenewable_energy: float,
        production_output: float,
        transport_distance: float,
        raw_material_usage: float,
        employment_count: float,
        sector: Optional[str] = None,
        industry_sector: Optional[str] = None,
        transport_mode: Optional[str] = None,
    ) -> dict:
        """Run the real XGBoost model for a what-if scenario (with optional sector, industry_sector, and transport_mode) and return predicted CO2 emissions."""
        return model_service.predict({
            "Total_Energy_Consumption_kWh": total_energy,
            "Renewable_Energy_Consumption_kWh": renewable_energy,
            "NonRenewable_Energy_Consumption_kWh": nonrenewable_energy,
            "Production_Output_Units": production_output,
            "Supply_Chain_Transport_km": transport_distance,
            "Raw_Material_Usage_kg": raw_material_usage,
            "Employment_Count": employment_count,
            "Sector": sector,
            "Industry_Sectors": industry_sector,
            "Supply_Chain_Transport_Mode": transport_mode,
        })

    def get_my_recent_predictions(limit: int = 5) -> list:
        """Fetch the logged-in user's recent saved CO2 prediction history from the database."""
        if user_id is None:
            return [{"note": "User is not logged in; no saved history available."}]
        with SessionLocal() as tool_db:
            rows = (
                tool_db.query(PredictionHistory)
                .filter(PredictionHistory.user_id == user_id)
                .order_by(PredictionHistory.created_at.desc())
                .limit(limit)
                .all()
            )
            return [
                {
                    "id": r.id,
                    "total_energy": r.total_energy,
                    "renewable_energy": r.renewable_energy,
                    "nonrenewable_energy": r.nonrenewable_energy,
                    "production_output": r.production_output,
                    "sector": getattr(r, "sector", None),
                    "industry_sector": getattr(r, "industry_sector", None),
                    "transport_mode": getattr(r, "transport_mode", None),
                    "predicted_co2": r.predicted_co2_emission,
                    "carbon_intensity": r.carbon_intensity,
                    "created_at": str(r.created_at),
                }
                for r in rows
            ]

    tools_map = {
        "get_sector_and_dataset_analytics": get_sector_and_dataset_analytics,
        "get_model_and_shap_insights": get_model_and_shap_insights,
        "run_whatif_prediction": run_whatif_prediction,
        "get_my_recent_predictions": get_my_recent_predictions,
    }

    def stream_turn_with_fallback(turn_contents, config):
        last_err = None
        for model_name in FALLBACK_MODELS:
            chunks_text = []
            try:
                tool_calls = []
                model_parts = []

                for chunk in client.models.generate_content_stream(
                    model=model_name,
                    contents=turn_contents,
                    config=config,
                ):
                    if chunk.function_calls:
                        tool_calls.extend(chunk.function_calls)
                    if chunk.candidates and chunk.candidates[0].content and chunk.candidates[0].content.parts:
                        model_parts.extend(chunk.candidates[0].content.parts)
                    if chunk.text:
                        chunks_text.append(chunk.text)
                        yield ("token", chunk.text)

                yield ("turn_end", (tool_calls, model_parts))
                return
            except Exception as e:
                last_err = e
                err_msg = str(e)
                if not chunks_text and any(code in err_msg for code in ("503", "429", "404", "UNAVAILABLE", "RESOURCE_EXHAUSTED")):
                    print(f"[CHATBOT] {model_name} unavailable, trying next model...", flush=True)
                    continue
                raise
        raise last_err

    def event_generator():
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            tools=list(tools_map.values()),
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            temperature=0.3,
        )

        full_answer = []
        try:
            while True:
                tool_calls_in_turn = []
                model_parts = []

                for kind, payload in stream_turn_with_fallback(contents, config):
                    if kind == "token":
                        full_answer.append(payload)
                        yield f"data: {json.dumps({'token': payload})}\n\n"
                    elif kind == "turn_end":
                        tool_calls_in_turn, model_parts = payload

                if not tool_calls_in_turn:
                    break

                contents.append(types.Content(role="model", parts=model_parts))
                tool_response_parts = []
                for fc in tool_calls_in_turn:
                    yield f"data: {json.dumps({'status': f'Running {fc.name}...'})}\n\n"
                    fn = tools_map.get(fc.name)
                    try:
                        result = fn(**(fc.args or {})) if fn else {"error": "Unknown tool"}
                    except Exception as e:
                        result = {"error": str(e)}

                    tool_response_parts.append(
                        types.Part.from_function_response(
                            name=fc.name,
                            response={"result": json.loads(json.dumps(result, default=str))},
                        )
                    )
                contents.append(types.Content(role="user", parts=tool_response_parts))

        except Exception as e:
            print("[CHATBOT ERROR]", repr(e), flush=True)
            traceback.print_exc()
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            return

        assistant_text = "".join(full_answer).strip()
        if assistant_text:
            with SessionLocal() as save_db:
                save_db.add(ChatMessage(
                    user_id=user_id,
                    session_id=req.session_id,
                    role="model",
                    content=assistant_text,
                ))
                save_db.commit()

        yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")