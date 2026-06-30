import random
from pathlib import Path

import requests

from .config import Settings
from .models import VideoPlan

MINIMAX_VOICES = [
    "English_expressive_narrator",
    "English_cheerful_female",
    "English_trustworthy_male",
    "English_young_female_voice",
    "English_male_deep_voice",
]


def generate_voice(plan: VideoPlan, output: Path, settings: Settings) -> Path:
    text = "\n".join(slide.narration for slide in plan.slides)
    provider = settings.tts_provider.lower()
    if provider == "minimax":
        _save_minimax(text, output, settings)
    elif provider == "ttsmaker":
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


def _save_minimax(text: str, output: Path, settings: Settings) -> None:
    if not settings.minimax_api_key:
        raise RuntimeError("TTS_PROVIDER=minimax icin .env dosyasinda MINIMAX_API_KEY gerekli.")
    url = "https://api.minimaxi.chat/v1/t2a_v2"
    headers = {
        "Authorization": f"Bearer {settings.minimax_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.minimax_model,
        "text": text,
        "stream": False,
        "voice_setting": {
            "voice_id": settings.minimax_voice_id or random.choice(MINIMAX_VOICES),
            "speed": settings.minimax_speed,
            "vol": settings.minimax_vol,
            "pitch": 0,
        },
        "audio_setting": {
            "sample_rate": 32000,
            "bitrate": 128000,
            "format": "mp3",
        },
    }
    response = requests.post(url, json=payload, headers=headers, timeout=120)
    response.raise_for_status()
    data = response.json()
    if data.get("base_resp", {}).get("status_code", 0) != 0:
        raise RuntimeError(f"MiniMax hata: {data['base_resp'].get('status_msg')}")
    audio_hex = data.get("data", {}).get("audio")
    if not audio_hex:
        raise RuntimeError("MiniMax ses verisi dondurmedi.")
    output.write_bytes(bytes.fromhex(audio_hex))


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