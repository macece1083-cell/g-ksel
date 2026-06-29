from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    provider: str = os.getenv("BOT_PROVIDER", "template")
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    anthropic_model: str = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    ollama_url: str = os.getenv("OLLAMA_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    image_provider: str = os.getenv("IMAGE_PROVIDER", "gemini")
    tts_provider: str = os.getenv("TTS_PROVIDER", "gtts")
    tts_voice: str = os.getenv("TTS_VOICE", "en-US-JennyNeural")
    ttsmaker_api_key: str = os.getenv("TTSMAKER_API_KEY", "")
    ttsmaker_voice_id: int = int(os.getenv("TTSMAKER_VOICE_ID", "1480"))
    ttsmaker_audio_speed: float = float(os.getenv("TTSMAKER_AUDIO_SPEED", "1"))
    ttsmaker_emotion_style_key: str = os.getenv("TTSMAKER_EMOTION_STYLE_KEY", "friendly")
    ttsmaker_high_quality: int = int(os.getenv("TTSMAKER_HIGH_QUALITY", "1"))
    video_width: int = int(os.getenv("VIDEO_WIDTH", "1920"))
    video_height: int = int(os.getenv("VIDEO_HEIGHT", "1080"))
    ffmpeg_path: str = os.getenv("FFMPEG_PATH", "")
    ffprobe_path: str = os.getenv("FFPROBE_PATH", "")
    default_privacy_status: str = os.getenv("DEFAULT_PRIVACY_STATUS", "private")
    youtube_client_secrets: str = os.getenv("YOUTUBE_CLIENT_SECRETS", "client_secret.json")
    youtube_token_file: str = os.getenv("YOUTUBE_TOKEN_FILE", "token.json")
    instagram_access_token: str = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
    instagram_user_id: str = os.getenv("INSTAGRAM_USER_ID", "")
    imgbb_api_key: str = os.getenv("IMGBB_API_KEY", "")
    minimax_api_key: str = os.getenv("MINIMAX_API_KEY", "")
    minimax_model: str = os.getenv("MINIMAX_MODEL", "speech-02-hd")
    minimax_voice_id: str = os.getenv("MINIMAX_VOICE_ID", "English_expressive_narrator")
    minimax_speed: float = float(os.getenv("MINIMAX_SPEED", "1.0"))
    minimax_vol: float = float(os.getenv("MINIMAX_VOL", "1.0"))


def output_dir() -> Path:
    path = ROOT / "output"
    path.mkdir(exist_ok=True)
    return path