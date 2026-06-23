import os
import time
import urllib.parse
import requests
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import io

from .config import Settings


def generate_image(prompt: str, output_path: Path, settings: Settings) -> Path:
    if settings.image_provider.lower() == "gemini":
        result = _gemini_image(prompt, output_path, settings)
        if result:
            return result
    return _pollinations_image(prompt, output_path, settings)


def _gemini_image(prompt: str, output_path: Path, settings: Settings) -> Path | None:
    try:
        enhanced = (
            f"{prompt}, educational style, clean modern design, "
            f"professional, vibrant colors, high quality"
        )
        url = "https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-001:predict"
        payload = {
            "instances": [{"prompt": enhanced}],
            "parameters": {"sampleCount": 1, "aspectRatio": "16:9"},
        }
        resp = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            params={"key": settings.gemini_api_key},
            timeout=60,
        )
        if resp.status_code == 200:
            data = resp.json()
            img_b64 = data["predictions"][0]["bytesBase64Encoded"]
            import base64
            img_bytes = base64.b64decode(img_b64)
            img = Image.open(io.BytesIO(img_bytes))
            img = img.resize((settings.video_width, settings.video_height))
            img.save(str(output_path))
            print(f"  Gemini gorsel: {output_path.name}")
            return output_path
        else:
            print(f"  Gemini hata {resp.status_code}: {resp.text[:200]}")
            return None
    except Exception as e:
        print(f"  Gemini kullanilamadi: {e}")
        return None


def _pollinations_image(prompt: str, output_path: Path, settings: Settings) -> Path:
    enhanced = (
        f"{prompt}, educational style, clean modern design, "
        f"professional, vibrant colors, high quality, 4K"
    )
    encoded = urllib.parse.quote(enhanced)
    url = (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?width={settings.video_width}&height={settings.video_height}&nologo=true&enhance=true"
    )
    for attempt in range(3):
        try:
            resp = requests.get(url, timeout=60)
            if resp.status_code == 200 and resp.headers.get("content-type", "").startswith("image"):
                output_path.write_bytes(resp.content)
                print(f"  Pollinations gorsel: {output_path.name}")
                return output_path
        except Exception as e:
            print(f"  Deneme {attempt+1}/3: {e}")
            time.sleep(2 ** attempt)
    return _placeholder(output_path, settings)


def _placeholder(output_path: Path, settings: Settings) -> Path:
    img = Image.new("RGB", (settings.video_width, settings.video_height), color=(30, 30, 50))
    draw = ImageDraw.Draw(img)
    draw.text((settings.video_width // 2, settings.video_height // 2), "English Learning",
              fill=(255, 255, 255), anchor="mm")
    img.save(str(output_path))
    return output_path


def generate_images(plan, run_dir: Path, settings: Settings) -> list[Path]:
    paths = []
    for i, slide in enumerate(plan.slides):
        out = run_dir / f"slide_{i:02d}.jpg"
        path = generate_image(slide.visual_prompt, out, settings)
        paths.append(path)
        time.sleep(0.5)
    return paths
