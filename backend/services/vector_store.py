from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    PayloadSchemaType,
)
from dotenv import load_dotenv
import os
import uuid

load_dotenv()

EMBEDDING_DIM = 1536
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "youtube_rag")

# Qdrant Cloud veya lokal — ikisini de destekler
qdrant_url = os.getenv("QDRANT_URL")
qdrant_api_key = os.getenv("QDRANT_API_KEY")
qdrant_host = os.getenv("QDRANT_HOST", "localhost")
qdrant_port = int(os.getenv("QDRANT_PORT", 6333))

if qdrant_url:
    # Qdrant Cloud
    client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key, timeout=60)
else:
    # Lokal Docker
    client = QdrantClient(host=qdrant_host, port=qdrant_port, timeout=60)

_collection_ready = False

def ensure_collection():
    global _collection_ready
    if _collection_ready:
        return
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME not in existing:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=EMBEDDING_DIM,
                distance=Distance.COSINE,
            ),
        )
    # Idempotent: index zaten varsa Qdrant sessizce geçer
    client.create_payload_index(
        collection_name=COLLECTION_NAME,
        field_name="video_id",
        field_schema=PayloadSchemaType.KEYWORD,
    )
    _collection_ready = True

def save_chunks(chunks: list[dict], embeddings: list[list[float]], video_id: str, video_url: str):
    ensure_collection()
    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={
                "text": chunk["text"],
                "start": chunk["start"],
                "video_id": video_id,
                "video_url": video_url,
                "youtube_link": f"{video_url}&t={chunk['start']}s",
            },
        )
        for chunk, embedding in zip(chunks, embeddings)
    ]
    client.upsert(collection_name=COLLECTION_NAME, points=points)

def search(query_embedding: list[float], video_id: str, top_k: int = 5) -> list[dict]:
    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_embedding,
        query_filter=Filter(
            must=[FieldCondition(key="video_id", match=MatchValue(value=video_id))]
        ),
        limit=top_k,
    )
    return [
        {
            "text": r.payload["text"],
            "start": r.payload["start"],
            "youtube_link": r.payload["youtube_link"],
            "score": round(r.score, 3),
        }
        for r in results
    ]

def video_exists(video_id: str) -> bool:
    ensure_collection()
    results = client.scroll(
        collection_name=COLLECTION_NAME,
        scroll_filter=Filter(
            must=[FieldCondition(key="video_id", match=MatchValue(value=video_id))]
        ),
        limit=1,
    )
    return len(results[0]) > 0