from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
import re

def extract_video_id(url: str) -> str:
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11})",
        r"(?:youtu\.be\/)([0-9A-Za-z_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError(f"Geçerli bir YouTube URL'si değil: {url}")

def get_transcript(url: str) -> list[dict]:
    video_id = extract_video_id(url)
    
    try:
        # v0.6.x+ instance API; older versions use the class method
        try:
            transcript_list = YouTubeTranscriptApi().list(video_id)
        except AttributeError:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        # Önce manuel, sonra otomatik transcript dene
        try:
            transcript = transcript_list.find_transcript(["tr", "en"])
        except NoTranscriptFound:
            transcript = transcript_list.find_generated_transcript(["tr", "en"])
        
        raw = transcript.fetch()
        
        result = []
        for segment in raw:
            # v0.6.x returns objects with attributes; older versions return dicts
            if hasattr(segment, "text"):
                text = segment.text.strip()
                start = round(segment.start)
            else:
                text = segment.get("text", "").strip()
                start = round(segment.get("start", 0))
            if text:
                result.append({"text": text, "start": start})
        return result
        
    except TranscriptsDisabled:
        raise ValueError("Bu videoda transcript kapalı.")
    except NoTranscriptFound:
        raise ValueError("Bu video için Türkçe veya İngilizce transcript bulunamadı.")
    except Exception as e:
        raise ValueError(f"Transcript alınırken hata oluştu: {str(e)}")