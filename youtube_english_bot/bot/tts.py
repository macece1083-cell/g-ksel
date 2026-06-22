import asyncio
import subprocess
import tempfile
from pathlib import Path

import requests

from .config import Settings
from .models import VideoPlan


def generate_voice(plan: VideoPlan, output: Path, settings: Settings) -> Path:
    text = "\n".join(slide.narration for slide in plan.slides)
    if settings.tts_provider.lower() == "ttsmaker":
        _save_ttsmaker(text, output, settings)
    else:
        try:
            _save_gtts(text, output)
        except Exception as exc:
            print(f"gTTS kullanilamadi: {exc}")
            raise
    return output


def _save_gtts(text: str, output: Path) -> None:
    from gtts import gTTS
    tts = gTTS(text=text, lang="en", slow=False)
    tts.save(str(output))


def _save_ttsmaker(text: str, output: Path, settings: Settings) -> None:
    if not settings.ttsmaker_api_key:
        raise RuntimeError("TTS_PROVIDER=ttsmaker icin .env dosyasinda TTSMAKER_API_KEY gerekli.")

    payload = {
        "api_key": settings.ttsmaker_api_key,
        "text": text,
        "voice_id": settings.ttsmaker_voice_id,
        "audio_format": "mp3",
        "audio_speed": settings.ttsmaker_audio_speed,
        "audio_volume": 1,
        "audio_pitch": 1,
        "audio_high_quality": settings.ttsmaker_high_quality,
        "text_paragraph_pause_time": 650,
        "emotion_style_key": settings.ttsmaker_emotion_style_key,
        "emotion_intensity": 1,
    }
    response = requests.post("https://api.ttsmaker.com/v2/create-tts-order", json=payload, timeout=120)
    response.raise_for_status()
    data = response.json()
    if data.get("error_code") != 0:
        raise RuntimeError(f"TTSMaker hata verdi: {data.get('error_summary') or data.get('msg')}")

    audio_url = data.get("audio_download_url") or data.get("audio_download_backup_url")
    if not audio_url:
        raise RuntimeError("TTSMaker ses indirme linki dondurmedi.")

    audio_response = requests.get(audio_url, timeout=120)
    audio_response.raise_for_status()
    output.write_bytes(audio_response.content)
