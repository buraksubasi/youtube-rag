from langchain_text_splitters import RecursiveCharacterTextSplitter
from services.transcript import get_transcript, extract_video_id
from services.embedder import embed_text, embed_batch
from services.vector_store import save_chunks, search, video_exists
from services.reranker import rerank

def chunk_transcript(segments: list[dict]) -> list[dict]:
    # Önce tüm segmentleri birleştir, timestamp'i koru
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=["\n\n", "\n", ". ", " "],
    )
    
    chunks = []
    current_text = ""
    current_start = 0
    
    for segment in segments:
        if not current_text:
            current_start = segment["start"]
        current_text += " " + segment["text"]
        
        # Her ~800 karakterde bir chunk oluştur
        if len(current_text) >= 800:
            chunks.append({
                "text": current_text.strip(),
                "start": current_start,
            })
            # 100 karakter overlap için sonu tut
            current_text = current_text[-100:]
            current_start = segment["start"]
    
    # Kalan metni ekle
    if current_text.strip():
        chunks.append({
            "text": current_text.strip(),
            "start": current_start,
        })
    
    return chunks

def ingest_video(url: str) -> dict:
    video_id = extract_video_id(url)
    
    # Daha önce işlendiyse tekrar embed etme
    if video_exists(video_id):
        return {"status": "already_exists", "video_id": video_id}
    
    # 1. Transcript çek
    segments = get_transcript(url)
    
    # 2. Chunk'la
    chunks = chunk_transcript(segments)
    
    # 3. Embed et
    texts = [c["text"] for c in chunks]
    embeddings = embed_batch(texts)
    
    # 4. Qdrant'a kaydet
    save_chunks(chunks, embeddings, video_id, url)
    
    return {
        "status": "success",
        "video_id": video_id,
        "chunk_count": len(chunks),
    }

def query_video(question: str, video_id: str) -> dict:
    query_embedding = embed_text(question)
    
    # Geniş net: top_k=10 aday getir
    candidates = search(query_embedding, video_id, top_k=10)
    
    # Re-rank: en alakalı 3'ü seç
    results = rerank(question, candidates, top_k=3)
    
    context = "\n\n".join([
        f"[{r['start']}. saniye]: {r['text']}"
        for r in results
    ])
    
    import google.generativeai as genai
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    prompt = f"""Aşağıda bir YouTube videosunun belirli bölümlerinden alınan transcript parçaları var.
Bu bilgilere dayanarak soruyu Türkçe olarak cevapla.
Cevabında hangi zaman diliminden bilgi aldığını belirt.
Eğer bilgi transcript'te yoksa "Bu videoda bu konuda bilgi bulamadım." de.

TRANSCRIPT PARÇALARI:
{context}

SORU: {question}

CEVAP:"""
    
    response = model.generate_content(prompt)
    
    return {
        "answer": response.text,
        "sources": results,
    }