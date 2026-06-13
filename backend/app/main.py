import os
os.environ["HF_HOME"] = r"D:\AIC\.cache\huggingface"
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from backend.app.services.search import SearchService
import os
import time
import json

app = FastAPI(title="AIC 2026 Video Retrieval Engine - P0 Baseline", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

search_service = SearchService()

# --- MODEL DEFINITIONS ---
class SearchRequest(BaseModel):
    query: str
    top_k: int = 100

class SubmitDryRunRequest(BaseModel):
    query_id: str
    video_id: str
    frame_id: str
    answer: str = None
    elapsed_ms: int

# --- ENDPOINTS ---
@app.get("/health")
def health_check():
    return {"status": "ok", "version": "P0-Baseline"}

@app.post("/api/v1/search")
def do_search(request: SearchRequest):
    return search_service.execute_textual_search(query_text=request.query, top_k=request.top_k)

@app.get("/api/v1/frame/neighbors")
def get_neighbors(
    video_id: str = Query(..., description="Tên/ID của video"), 
    frame_id: str = Query(..., description="Mã frame hiện tại (ví dụ: 0045)")
):
    return search_service.get_frame_neighbors(video_title=video_id, current_frame_id=frame_id)

@app.post("/api/v1/submit/dry-run")
def submit_dry_run(request: SubmitDryRunRequest):
    """
    Endpoint giả lập submit lên hệ thống DRES của BTC.
    Ghi lại log lịch sử để phục vụ việc tính toán Recall và Error Analysis.
    """
    LOG_DIR = "data/logs"
    os.makedirs(LOG_DIR, exist_ok=True)
    log_path = os.path.join(LOG_DIR, "submission_dry_run.jsonl")
    
    log_entry = {
        "query_id": request.query_id,
        "video_id": request.video_id,
        "frame_id": request.frame_id,
        "answer": request.answer,
        "elapsed_ms": request.elapsed_ms,
        "created_at": int(time.time() * 1000)
    }
    
    # Ghi file dưới dạng JSONL (Append)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        
    print(f"💾 [Log Submit] Đã lưu vết câu {request.query_id} -> Video: {request.video_id}, Frame: {request.frame_id}")
    return {"status": "success", "message": "Dry-run submission logged successfully", "data": log_entry}

# --- MEDIA SERVING ---
DATA_PROCESSED_DIR = r"D:\AIC\data\processed"
if os.path.exists(DATA_PROCESSED_DIR):
    app.mount("/media", StaticFiles(directory=DATA_PROCESSED_DIR), name="media")
    print(f"📁 [Media Serving] Đã kích hoạt mỏ ảnh tĩnh tại: {DATA_PROCESSED_DIR}")
else:
    print("⚠️ [Cảnh báo] Chưa tìm thấy thư mục data/processed để serve ảnh!")