import { ExternalLink, Clock } from "lucide-react";

interface Source {
  text: string;
  start: number;
  youtube_link: string;
  score: number;
}

export default function SourceCard({ source }: { source: Source }) {
  const formatTime = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s.toString().padStart(2, "0")}`;
  };

  return (
    <div className="border border-gray-200 rounded-lg p-3 text-sm hover:border-gray-300 transition-colors">
      <p className="text-gray-600 line-clamp-2 mb-2">{source.text}</p>
      <div className="flex items-center justify-between">
        <span className="flex items-center gap-1 text-gray-400 text-xs">
          <Clock size={12} />
          {formatTime(source.start)}
        </span>
        
        <a href={source.youtube_link} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1 text-red-500 hover:text-red-600 text-xs font-medium">
          Videoda gör
          <ExternalLink size={12} />
        </a>
      </div>
    </div>
   
  );
}