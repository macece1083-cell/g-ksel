import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from .config import Settings, output_dir
from .content import create_video_plan
from .curriculum import get_lesson
from .images import generate_images
from .tts import generate_voice
from .video import compose_video
from .youtube import upload_video


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", default="A1", choices=["A1", "A2", "B1", "B2", "C1", "C2"])
    parser.add_argument("--topic", default="auto")
    parser.add_argument("--mode", default="general", choices=["general", "meb"])
    parser.add_argument("--upload", action="store_true")
    parser.add_argument("--playlist", default="")
    parser.add_argument("--day", type=int, default=0)
    args = parser.parse_args()

    settings = Settings()

    if args.mode == "meb":
        day = args.day if args.day > 0 else datetime.now(timezone.utc).timetuple().tm_yday
        lesson = get_lesson(day)
        topic = f"MEB 5th grade Unit {lesson['unit']}: {lesson['topic']} - {lesson['outcome']}"
        level = "A1"
        print(f"MEB Dersi: {topic}")
    else:
        topic = args.topic
        level = args.level

    plan = create_video_plan(level, topic, settings)
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
        url = upload_video(video, plan, settings, playlist_id=args.playlist)
        print(f"YouTube yuklendi: {url}")


def _slug(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]+", "-", value).strip("-").lower()
