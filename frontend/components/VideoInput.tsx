"use client";

import { useState } from "react";
import { PlayCircle, Loader2 } from "lucide-react";
import { ingestVideo } from "@/lib/api";

interface Props {
  onVideoReady: (videoId: string, videoUrl: string) => void;
}

export default function VideoInput({ onVideoReady }: Props) {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [status, setStatus] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;

    setLoading(true);
    setError("");
    setStatus("");

    try {
      const result = await ingestVideo(url);

      if (result.status === "already_exists") {
        setStatus("Video zaten işlenmiş, soru sorabilirsiniz.");
      } else {
        setStatus(`${result.chunk_count} parça işlendi, soru sorabilirsiniz.`);
      }

      onVideoReady(result.video_id, url);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full">
      <form onSubmit={handleSubmit} className="flex gap-2">
        <div className="flex-1 relative">
          <PlayCircle
            size={18}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-red-500"
          />
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="YouTube URL yapıştır..."
            className="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-lg text-sm text-gray-900 bg-white placeholder:text-gray-400 focus:outline-none focus:border-gray-400 transition-colors"
          />
        </div>
        <button
          type="submit"
          disabled={loading || !url.trim()}
          className="px-4 py-2.5 bg-gray-900 text-white text-sm rounded-lg hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
        >
          {loading ? <Loader2 size={16} className="animate-spin" /> : null}
          {loading ? "İşleniyor..." : "Yükle"}
        </button>
      </form>

      {error && (
        <p className="mt-2 text-sm text-red-500">{error}</p>
      )}
      {status && (
        <p className="mt-2 text-sm text-green-600">{status}</p>
      )}
    </div>
  );
}