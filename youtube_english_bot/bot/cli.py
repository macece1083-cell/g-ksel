import argparse
import json
import re
from datetime import datetime
from pathlib import Path

from .config import Settings, output_dir
from .content import create_video_plan
from .images import generate_images
from .tts import generate_voice
from .video import compose_video
from .youtube import upload_video


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate English learning videos for YouTube.")
    parser.add_argument("--level", default="A1", choices=["A1", "A2", "B1", "B2", "C1", "C2"])
    parser.add_argument("--topic", default="daily vocabulary")
    parser.add_argument("--upload", action="store_true")
    parser.add_argument("--no-images", action="store_true", help="Use local placeholder images instead of AI image API.")
    args = parser.parse_args()

    settings = Settings()
    if args.no_images:
        settings = Settings(image_provider="placeholder")

    plan = create_video_plan(args.level, args.topic, settings)
    run_dir = output_dir() / f"{datetime.now():%Y%m%d_%H%M%S}_{_slug(plan.level + '_' + plan.topic)}"
    run_dir.mkdir(parents=True, exist_ok=True)

    metadata_path = run_dir / "metadata.json"
    metadata_path.write_text(json.dumps(plan, default=lambda item: item.__dict__, indent=2), encoding="utf-8")
    print(f"Icerik plani hazir: {metadata_path}")

    images = generate_images(plan, run_dir, settings)
    print(f"{len(images)} gorsel hazir.")

    audio = generate_voice(plan, run_dir / "voice.mp3", settings)
    print(f"Ses hazir: {audio}")

    video = compose_video(images, audio, run_dir / "video.mp4", settings)
    print(f"Video hazir: {video}")

    if args.upload:
        url = upload_video(video, plan, settings)
        print(f"YouTube yuklendi: {url}")


def _slug(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]+", "-", value).strip("-").lower()
