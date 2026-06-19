from flashrank import Ranker, RerankRequest

_ranker = None

def get_reranker():
    global _ranker
    if _ranker is None:
        print("Re-ranker model yükleniyor...")
        _ranker = Ranker(model_name="ms-marco-MultiBERT-L-12")
        print("Re-ranker model yüklendi.")
    return _ranker

def rerank(query: str, chunks: list[dict], top_k: int = 3) -> list[dict]:
    if not chunks:
        return []
    
    ranker = get_reranker()
    
    passages = [
        {"id": i, "text": chunk["text"], "meta": chunk}
        for i, chunk in enumerate(chunks)
    ]
    
    request = RerankRequest(query=query, passages=passages)
    ranked = ranker.rerank(request)
    
    result = []
    for item in ranked[:top_k]:
        chunk_copy = item["meta"].copy()
        chunk_copy["rerank_score"] = round(float(item["score"]), 6)
        result.append(chunk_copy)
    
    return result