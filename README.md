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

## Kurulum ve Çalıştırma

### Gereksinimler

| Servis | Açıklama | Link |
|---|---|---|
| Gemini API Key | Embedding + LLM için | [aistudio.google.com](https://aistudio.google.com/) |
| Qdrant Cloud | Vektör veritabanı | [cloud.qdrant.io](https://cloud.qdrant.io/) |
| Webshare (opsiyonel) | Cloud deploy'da YouTube IP bloğunu aşmak için | [webshare.io](https://www.webshare.io/) |

### Ortam Değişkenleri

`backend/.env` dosyası oluşturun:

```env
GEMINI_API_KEY=...
QDRANT_URL=https://<cluster>.cloud.qdrant.io
QDRANT_API_KEY=...
COLLECTION_NAME=youtube_rag
WEBSHARE_PROXY_USERNAME=     # opsiyonel — Render/cloud deploy için
WEBSHARE_PROXY_PASSWORD=     # opsiyonel — Render/cloud deploy için
```

`frontend/.env.local` dosyası oluşturun:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Local Geliştirme

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend (ayrı terminal)
cd frontend
npm install
npm run dev
```

---

## Cloud Deploy (Render)

### Neden Webshare Gerekli?

YouTube, AWS/GCP/Render gibi cloud provider IP'lerinden gelen transcript isteklerini engeller. Bu nedenle Render'a deploy edilmiş backend, proxy olmadan transcript çekemez.

### Webshare Kurulumu

1. [webshare.io](https://www.webshare.io/) adresine gidin ve ücretsiz hesap açın (Free plan: 10 proxy, 1 GB/ay)
2. Dashboard → **Proxy** → **Proxy Settings** bölümüne gidin
3. `Proxy Username` ve `Proxy Password` değerlerini kopyalayın

### Render'a Environment Variable Ekleme

Render Dashboard → Servisiniz → **Environment** sekmesine şu değişkenleri ekleyin:

```
GEMINI_API_KEY         = <değer>
QDRANT_URL             = <değer>
QDRANT_API_KEY         = <değer>
COLLECTION_NAME        = youtube_rag
WEBSHARE_PROXY_USERNAME = <webshare kullanıcı adı>
WEBSHARE_PROXY_PASSWORD = <webshare şifre>
```

Proxy credentials ayarlandığında kod otomatik olarak Webshare üzerinden istek atar. Credentials eksikse (local ortam) direkt bağlantı kullanılır — local geliştirmede ek bir ayar gerekmez.

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
