# YouTube Video Soru-Cevap Sistemi (RAG Mimarisi)

## Akış

### 1. Video İşleme Süreci

Kullanıcı bir YouTube URL'i girer.

```text
Kullanıcı URL girer
    ↓
Backend transcript'i çeker (youtube-transcript-api)
    ↓
Metin anlamlı chunk'lara bölünür
    ↓
Her chunk Gemini Embedding API ile vektöre dönüştürülür
    ↓
Embedding'ler ve metadata Qdrant'a kaydedilir
```

### İşlenen Veri Örneği

```json
{
  "videoId": "abc123",
  "timestamp": "05:32",
  "text": "React uygulamalarında performans optimizasyonu...",
  "embedding": [0.123, 0.456, ...]
}
```

---

## 2. Soru-Cevap Süreci

Kullanıcı videoyla ilgili bir soru sorar.

```text
Kullanıcı soru sorar
    ↓
Soru Gemini Embedding API ile embed edilir
    ↓
Qdrant'ta similarity search yapılır
    ↓
En alakalı chunk'lar bulunur
    ↓
Chunk'lar + Kullanıcı Sorusu Gemini'ye gönderilir
    ↓
Gemini cevap üretir
    ↓
Timestamp referansları ile birlikte sonuç döner
```

---

## Örnek Sorgu Akışı

### Kullanıcı Sorusu

```text
Videoda React performansı hakkında ne anlatılıyor?
```

### Retrieval

Qdrant'tan en alakalı chunk'lar çekilir:

```text
[05:32]
React uygulamalarında gereksiz render'ların önüne geçmek için memoization kullanılabilir.

[08:14]
useMemo ve useCallback hook'ları performans optimizasyonunda önemli rol oynar.
```

### Gemini Prompt

```text
Aşağıdaki içerikleri kullanarak soruyu cevapla.

İçerik:
[05:32] React uygulamalarında gereksiz render'ların önüne geçmek için memoization kullanılabilir.

[08:14] useMemo ve useCallback hook'ları performans optimizasyonunda önemli rol oynar.

Soru:
Videoda React performansı hakkında ne anlatılıyor?
```

### Sonuç

```json
{
  "answer": "Videoda React performansını artırmak için memoization teknikleri, useMemo ve useCallback hook'larının kullanımı anlatılıyor.",
  "references": [
    {
      "timestamp": "05:32"
    },
    {
      "timestamp": "08:14"
    }
  ]
}
```

---

## Kullanılan Teknolojiler

* YouTube Transcript API
* Gemini Embedding API
* Gemini LLM
* Qdrant Vector Database
* Backend API (.NET / Node.js / Python)
* Retrieval-Augmented Generation (RAG)

---

## Mimari Diyagram

```text
                ┌─────────────────┐
                │ YouTube URL     │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Transcript Çek  │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Chunking        │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Gemini Embed    │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Qdrant          │
                └────────┬────────┘
                         │
─────────────────────────┼─────────────────────────

                Kullanıcı Soru Sorar

─────────────────────────┼─────────────────────────
                         │
                         ▼
                ┌─────────────────┐
                │ Soru Embed      │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Qdrant Search   │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Gemini Answer   │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Cevap +         │
                │ Timestamp       │
                └─────────────────┘
```
