import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from .config import Settings, output_dir
from .content import create_video_plan
from .curriculum import get_lesson
from .images import generate_images
from .instagram import create_instagram_image, post_to_instagram
from .tts import generate_voice
from .video import compose_video
from .youtube import upload_video

MEB_MODES = {
    "meb":  {"grade": 5, "level": "A1", "label": "5th grade"},
    "meb6": {"grade": 6, "level": "A2", "label": "6th grade"},
    "meb7": {"grade": 7, "level": "A2", "label": "7th grade"},
    "lgs8": {"grade": 8, "level": "B1", "label": "8th grade LGS"},
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", default="A1", choices=["A1", "A2", "B1", "B2", "C1", "C2"])
    parser.add_argument("--topic", default="auto")
    parser.add_argument("--mode", default="general", choices=["general", "meb", "meb6", "meb7", "lgs8"])
    parser.add_argument("--upload", action="store_true")
    parser.add_argument("--instagram", action="store_true")
    parser.add_argument("--playlist", default="")
    parser.add_argument("--day", type=int, default=0)
    args = parser.parse_args()

    settings = Settings()

    if args.mode in MEB_MODES:
        cfg = MEB_MODES[args.mode]
        day = args.day if args.day > 0 else datetime.now(timezone.utc).timetuple().tm_yday
        lesson = get_lesson(day, grade=cfg["grade"])
        topic = f"MEB {cfg['label']} Unit {lesson['unit']}: {lesson['topic']} - {lesson['outcome']}"
        level = cfg["level"]
        print(f"MEB Dersi: {topic}")
    else:
        topic = args.topic
        if args.level == "A1":
            levels = ["A1", "A2", "B1", "B2", "C1", "C2"]
            level = levels[datetime.now(timezone.utc).timetuple().tm_yday % len(levels)]
            print(f"General mod seviyesi: {level}")
        else:
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

    youtube_url = ""
    if args.upload:
        youtube_url = upload_video(video, plan, settings, playlist_id=args.playlist)
        print(f"YouTube yuklendi: {youtube_url}")

    if args.instagram and settings.instagram_access_token and settings.instagram_user_id:
        ig_image = create_instagram_image(plan, run_dir)
        print(f"Instagram gorseli hazir: {ig_image}")
        post_id = post_to_instagram(
            plan=plan,
            image_path=ig_image,
            ig_token=settings.instagram_access_token,
            ig_user_id=settings.instagram_user_id,
            imgbb_api_key=settings.imgbb_api_key,
            youtube_url=youtube_url,
        )
        print(f"Instagram post atildi: {post_id}")
    elif args.instagram:
        print("Instagram ayarlari eksik, post atlamiyor.")


def _slug(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]+", "-", value).strip("-").lower()