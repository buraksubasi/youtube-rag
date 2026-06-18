from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models.schemas import (
    IngestRequest,
    IngestResponse,
    QueryRequest,
    QueryResponse,
    VideoStatusResponse,
)
from contextlib import asynccontextmanager
from services.rag import ingest_video, query_video
from services.transcript import extract_video_id
from services.vector_store import video_exists, ensure_collection
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_collection()
    yield

app = FastAPI(title="YouTube RAG API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://youtube-rag-nu.vercel.app",  # deploy sonrası güncellenecek
        os.getenv("FRONTEND_URL", ""),
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/ingest", response_model=IngestResponse)
async def ingest(request: IngestRequest):
    try:
        result = ingest_video(request.url)
        
        if result["status"] == "already_exists":
            return IngestResponse(
                status="already_exists",
                video_id=result["video_id"],
                message="Bu video daha önce işlendi, direkt soru sorabilirsiniz.",
            )
        
        return IngestResponse(
            status="success",
            video_id=result["video_id"],
            chunk_count=result["chunk_count"],
            message=f"{result['chunk_count']} parça başarıyla işlendi.",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()  # terminalde tam hata görünür
        raise HTTPException(status_code=500, detail=f"Beklenmeyen hata: {str(e)}")

@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    try:
        if not video_exists(request.video_id):
            raise HTTPException(
                status_code=404,
                detail="Bu video henüz işlenmedi. Önce /ingest endpoint'ini kullanın.",
            )
        
        result = query_video(request.question, request.video_id)
        return QueryResponse(
            answer=result["answer"],
            sources=result["sources"],
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Beklenmeyen hata: {str(e)}")

@app.get("/video/{video_id}/status", response_model=VideoStatusResponse)
def video_status(video_id: str):
    return VideoStatusResponse(
        video_id=video_id,
        exists=video_exists(video_id),
    )