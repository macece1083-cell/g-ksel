import json
import os
import shutil
import subprocess
from pathlib import Path

from .config import Settings


def compose_video(images: list[Path], audio: Path, output: Path, settings: Settings) -> Path:
    ffmpeg = _find_binary("ffmpeg", settings.ffmpeg_path)
    ffprobe = _find_binary("ffprobe", settings.ffprobe_path)
    duration = _audio_duration(audio, ffprobe)
    per_slide = max(duration / max(len(images), 1), 3.5)
    concat_file = output.with_suffix(".concat.txt")
    concat_file.write_text(
        "".join(f"file '{image.as_posix()}'\nduration {per_slide:.3f}\n" for image in images)
        + f"file '{images[-1].as_posix()}'\n",
        encoding="utf-8",
    )
    cmd = [
        ffmpeg,
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_file),
        "-i",
        str(audio),
        "-vf",
        f"fps=25,scale={settings.video_width}:{settings.video_height}:force_original_aspect_ratio=decrease,"
        f"pad={settings.video_width}:{settings.video_height}:(ow-iw)/2:(oh-ih)/2,format=yuv420p",
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "20",
        "-c:a",
        "aac",
        "-shortest",
        str(output),
    ]
    subprocess.run(cmd, check=True)
    return output


def _audio_duration(audio: Path, ffprobe: str) -> float:
    result = subprocess.run(
        [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            str(audio),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return float(json.loads(result.stdout)["format"]["duration"])


def _find_binary(name: str, configured_path: str = "") -> str:
    if configured_path and Path(configured_path).exists():
        return configured_path
    found = shutil.which(name)
    if found:
        return found
    winget_root = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WinGet" / "Packages"
    matches = list(winget_root.glob(f"**/{name}.exe")) if winget_root.exists() else []
    if matches:
        return str(matches[0])
    try:
        subprocess.run([name, "-version"], check=True, capture_output=True)
        return name
    except (OSError, subprocess.CalledProcessError) as exc:
        raise RuntimeError(
            f"{name} bulunamadi. Windows icin winget install Gyan.FFmpeg komutuyla kurabilirsiniz."
        ) from exc
