"use client";

import { useState } from "react";
import VideoInput from "@/components/VideoInput";
import ChatBox from "@/components/ChatBox";
import { PlayCircle } from "lucide-react";

export default function Home() {
  const [videoId, setVideoId] = useState<string | null>(null);
  const [videoUrl, setVideoUrl] = useState<string>("");
  const [pendingQuestion, setPendingQuestion] = useState<string | null>(null);

  return (
    <main className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-3xl mx-auto flex items-center gap-2">
          <PlayCircle size={22} className="text-red-500" />
          <h1 className="font-semibold text-gray-900">YouTube RAG</h1>
        </div>
      </header>

      <div className="flex-1 max-w-3xl mx-auto w-full flex flex-col p-6 gap-4">
        {/* Video input */}
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <p className="text-sm text-gray-500 mb-3">
            Bir YouTube videosu yükle, içeriği hakkında soru sor.
          </p>
          <VideoInput
            onVideoReady={(id, url) => {
              setVideoId(id);
              setVideoUrl(url);
            }}
            onQuickQuestion={(q) => {
              setPendingQuestion(q);
            }}
          />
          {videoUrl && (
            <div className="mt-3 pt-3 border-t border-gray-100">
              <iframe
                src={`https://www.youtube.com/embed/${videoId}`}
                className="w-full aspect-video rounded-lg"
                allowFullScreen
              />
            </div>
          )}
        </div>

        {/* Chat */}
        {videoId && (
          <div className="bg-white rounded-xl border border-gray-200 flex-1 flex flex-col min-h-[500px]">
            <ChatBox
              videoId={videoId}
              pendingQuestion={pendingQuestion}
              onPendingQuestionConsumed={() => setPendingQuestion(null)}
            />
          </div>
        )}

        {!videoId && (
          <div className="flex-1 flex items-center justify-center text-gray-400 text-sm">
            Başlamak için bir YouTube URL'si yapıştır.
          </div>
        )}
      </div>
    </main>
  );
}