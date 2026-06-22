import argparse
import random
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]
TOPICS = [
    "daily vocabulary",
    "grammar",
    "pronunciation",
    "phrasal verbs",
    "idioms",
    "common mistakes",
    "listening practice",
]


def run_once(upload: bool) -> None:
    level = random.choice(LEVELS)
    topic = random.choice(TOPICS)
    cmd = [
        sys.executable,
        str(Path(__file__).with_name("main.py")),
        "--level",
        level,
        "--topic",
        topic,
    ]
    if upload:
        cmd.append("--upload")
    subprocess.run(cmd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the YouTube English bot every day.")
    parser.add_argument("--hour", type=int, default=10, help="Local hour to publish, 0-23.")
    parser.add_argument("--upload", action="store_true", help="Upload generated videos to YouTube.")
    parser.add_argument("--run-now", action="store_true", help="Generate one video immediately, then continue.")
    args = parser.parse_args()

    if args.run_now:
        run_once(args.upload)

    while True:
        now = datetime.now()
        if now.hour == args.hour and now.minute == 0:
            run_once(args.upload)
            time.sleep(70)
        time.sleep(20)


if __name__ == "__main__":
    main()
