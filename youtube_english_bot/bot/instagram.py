import base64
import json
import textwrap
import time
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .models import VideoPlan


def _make_square_image(plan: VideoPlan, out_path: Path) -> Path:
    size = 1080
    img = Image.new("RGB", (size, size), color=(30, 60, 120))
    draw = ImageDraw.Draw(img)

    for i in range(size):
        r = int(30 + (i / size) * 40)
        g = int(60 + (i / size) * 30)
        b = int(120 + (i / size) * 60)
        draw.line([(0, i), (size, i)], fill=(r, g, b))

    draw.ellipse([size - 300, -100, size + 100, 300], fill=(255, 200, 0))
    draw.ellipse([-100, size - 300, 300, size + 100], fill=(255, 100, 50))

    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 64)
        sub_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
    except Exception:
        title_font = ImageFont.load_default()
        sub_font = title_font
        small_font = title_font

    draw.text((60, 60), f"English {plan.level}", font=sub_font, fill=(255, 220, 50))

    y = 180
    for line in textwrap.wrap(plan.title, width=22)[:4]:
        draw.text((60, y), line, font=title_font, fill=(255, 255, 255))
        y += 80

    if plan.slides:
        snippet = plan.slides[0].narration[:120] + "..."
        y = max(y + 40, 560)
        for line in textwrap.wrap(snippet, width=38)[:4]:
            draw.text((60, y), line, font=small_font, fill=(200, 230, 255))
            y += 42

    draw.text((60, size - 90), "Learn English Every Day", font=sub_font, fill=(255, 220, 50))

    img.save(out_path, "JPEG", quality=90)
    return out_path


def _build_caption(plan: VideoPlan, youtube_url: str = "") -> str:
    level_emoji = {"A1": "🌱", "A2": "🌿", "B1": "🌳", "B2": "🌲", "C1": "🎯", "C2": "🏆"}.get(plan.level, "📚")
    lines = [
        f"{level_emoji} {plan.title}",
        "",
        "Bugün ne öğreniyoruz? / What are we learning today?",
    ]
    for slide in (plan.slides or [])[:3]:
        if slide.caption:
            lines.append(f"✅ {slide.caption}")
    lines += ["", "Tam video YouTube da! / Full video on YouTube!"]
    if youtube_url:
        lines.append(youtube_url)
    lines += [
        "",
        "#LearnEnglish #Ingilizce #EnglishLesson #ESL",
        f"#English{plan.level} #IngilizceOgren #DailyEnglish",
        "#kids #students #education #ogrenci",
    ]
    return "\n".join(lines)


def _upload_to_imgbb(image_path: Path, api_key: str) -> str:
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    data = urllib.parse.urlencode({"key": api_key, "image": b64}).encode()
    req = urllib.request.Request("https://api.imgbb.com/1/upload", data=data, method="POST")
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
    return result["data"]["url"]


def _ig_api(token: str, path: str, data: dict) -> dict:
    url = f"https://graph.instagram.com/v21.0{path}"
    payload = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def create_instagram_image(plan: VideoPlan, run_dir: Path) -> Path:
    out = run_dir / "instagram.jpg"
    return _make_square_image(plan, out)


def post_to_instagram(
    plan: VideoPlan,
    image_path: Path,
    ig_token: str,
    ig_user_id: str,
    imgbb_api_key: str,
    youtube_url: str = "",
) -> str:
    print("Instagram: gorsel ImgBB ye yukleniyor...")
    image_url = _upload_to_imgbb(image_path, imgbb_api_key)
    print(f"Instagram: gorsel URL: {image_url}")

    caption = _build_caption(plan, youtube_url)

    print("Instagram: medya container olusturuluyor...")
    container = _ig_api(ig_token, f"/{ig_user_id}/media", {
        "image_url": image_url,
        "caption": caption,
        "access_token": ig_token,
    })
    creation_id = container["id"]

    time.sleep(5)

    print("Instagram: post yayinlaniyor...")
    result = _ig_api(ig_token, f"/{ig_user_id}/media_publish", {
        "creation_id": creation_id,
        "access_token": ig_token,
    })
    post_id = result.get("id", "")
    print(f"Instagram: yayinlandi, post ID: {post_id}")
    return post_id