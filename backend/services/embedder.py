import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

EMBEDDING_MODEL = "models/gemini-embedding-001"
EMBEDDING_DIM = 1536  # dengeli seçim

def embed_text(text: str) -> list[float]:
    result = genai.embed_content(
        model=EMBEDDING_MODEL,
        content=text,
        output_dimensionality=EMBEDDING_DIM,
    )
    return result["embedding"]

def embed_batch(texts: list[str]) -> list[list[float]]:
    # Gemini batch embedding — tek tek çağırmaktan daha verimli
    embeddings = []
    for text in texts:
        embeddings.append(embed_text(text))
    return embeddings