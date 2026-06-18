from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
import os
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

def _build_api() -> YouTubeTranscriptApi:
    proxy_username = os.getenv("WEBSHARE_PROXY_USERNAME")
    proxy_password = os.getenv("WEBSHARE_PROXY_PASSWORD")

    if proxy_username and proxy_password:
        try:
            from youtube_transcript_api.proxies import WebshareProxyConfig
            return YouTubeTranscriptApi(
                proxy_config=WebshareProxyConfig(
                    proxy_username=proxy_username,
                    proxy_password=proxy_password,
                )
            )
        except ImportError:
            pass

    return YouTubeTranscriptApi()

def get_transcript(url: str) -> list[dict]:
    video_id = extract_video_id(url)
    
    try:
        api = _build_api()

        try:
            transcript_list = api.list(video_id)
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