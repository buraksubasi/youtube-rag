from pydantic import BaseModel, HttpUrl

class IngestRequest(BaseModel):
    url: str

class IngestResponse(BaseModel):
    status: str
    video_id: str
    chunk_count: int | None = None
    message: str | None = None

class QueryRequest(BaseModel):
    question: str
    video_id: str

class QueryResponse(BaseModel):
    answer: str
    sources: list[dict]

class VideoStatusResponse(BaseModel):
    video_id: str
    exists: bool