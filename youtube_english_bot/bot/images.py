from pathlib import Path
from urllib.parse import quote

import requests
from PIL import Image, ImageDraw, ImageFont

from .config import Settings
from .models import VideoPlan


def generate_images(plan: VideoPlan, workdir: Path, settings: Settings) -> list[Path]:
    paths: list[Path] = []
    for index, slide in enumerate(plan.slides, start=1):
        path = workdir / f"slide_{index:02d}.jpg"
        if settings.image_provider.lower() == "pollinations":
            _download_pollinations(slide.visual_prompt, path, settings)
        else:
            _placeholder_image(slide.visual_prompt, path, settings)
        _add_caption(path, slide.caption, plan.level, settings)
        paths.append(path)
    return paths


def _download_pollinations(prompt: str, path: Path, settings: Settings) -> None:
    encoded = quote(prompt)
    url = (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?width={settings.video_width}&height={settings.video_height}&nologo=true&enhance=true"
    )
    response = requests.get(url, timeout=90)
    response.raise_for_status()
    path.write_bytes(response.content)


def _placeholder_image(prompt: str, path: Path, settings: Settings) -> None:
    image = Image.new("RGB", (settings.video_width, settings.video_height), "#243447")
    draw = ImageDraw.Draw(image)
    title_font = _font(82)
    body_font = _font(44)
    draw.rectangle([80, 80, settings.video_width - 80, settings.video_height - 80], outline="#f6c445", width=8)
    draw.text((140, 170), "English Practice", font=title_font, fill="white")
    draw.line([140, 280, 680, 280], fill="#f6c445", width=8)
    for idx, line in enumerate(_wrap(prompt, 52)[:4]):
        draw.text((140, 340 + idx * 66), line, font=body_font, fill="#dbe7f0")
    image.save(path, quality=92)


def _add_caption(path: Path, caption: str, level: str, settings: Settings) -> None:
    image = Image.open(path).convert("RGB").resize((settings.video_width, settings.video_height))
    draw = ImageDraw.Draw(image, "RGBA")
    title_font = _font(74)
    badge_font = _font(48)
    lines = _wrap(caption, 34)
    box_height = 150 + (len(lines) - 1) * 82
    y0 = settings.video_height - box_height - 80
    draw.rounded_rectangle([100, y0, settings.video_width - 100, settings.video_height - 80], radius=28, fill=(8, 18, 28, 205))
    draw.rounded_rectangle([130, y0 + 30, 250, y0 + 110], radius=18, fill=(246, 196, 69, 245))
    draw.text((157, y0 + 42), level, font=badge_font, fill=(20, 24, 28, 255))
    for idx, line in enumerate(lines):
        draw.text((290, y0 + 36 + idx * 82), line, font=title_font, fill=(255, 255, 255, 255))
    image.save(path, quality=94)


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _wrap(text: str, width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        if len(f"{current} {word}".strip()) > width and current:
            lines.append(current)
            current = word
        else:
            current = f"{current} {word}".strip()
    if current:
        lines.append(current)
    return lines[:3]
