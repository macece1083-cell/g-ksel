import asyncio
import subprocess
from pathlib import Path

import edge_tts
import requests

from .config import Settings
from .models import VideoPlan


def generate_voice(plan: VideoPlan, output: Path, settings: Settings) -> Path:
    text = "\n".join(slide.narration for slide in plan.slides)
    if settings.tts_provider.lower() == "ttsmaker":
        _save_ttsmaker(text, output, settings)
    elif settings.tts_provider.lower() == "sapi":
        output = output.with_suffix(".wav")
        _save_windows_sapi(text, output)
    else:
        try:
            asyncio.run(_save_edge_voice(text, output, settings.tts_voice))
        except Exception as exc:
            print(f"Edge TTS kullanilamadi, Windows SAPI'ye geciliyor: {exc}")
            output = output.with_suffix(".wav")
            _save_windows_sapi(text, output)
    return output


async def _save_edge_voice(text: str, output: Path, voice: str) -> None:
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(output))


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


def _save_windows_sapi(text: str, output: Path) -> None:
    text_path = output.with_suffix(".txt")
    text_path.write_text(text, encoding="utf-8")
    script = f"""
Add-Type -AssemblyName System.Speech
$text = Get-Content -LiteralPath '{_ps_escape(str(text_path))}' -Raw
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.Rate = 0
$synth.Volume = 100
$synth.SetOutputToWaveFile('{_ps_escape(str(output))}')
$synth.Speak($text)
$synth.Dispose()
"""
    subprocess.run(["powershell", "-NoProfile", "-Command", script], check=True, capture_output=True, text=True)
    text_path.unlink(missing_ok=True)


def _ps_escape(value: str) -> str:
    return value.replace("'", "''")
