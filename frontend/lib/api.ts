const API_URL = process.env.NEXT_PUBLIC_API_URL;

export async function ingestVideo(url: string) {
  const res = await fetch(`${API_URL}/ingest`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Video işlenirken hata oluştu.");
  }

  return res.json();
}

export async function queryVideo(question: string, videoId: string) {
  const res = await fetch(`${API_URL}/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, video_id: videoId }),
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Soru sorulurken hata oluştu.");
  }

  return res.json();
}