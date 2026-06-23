from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from .config import ROOT, Settings
from .models import VideoPlan

SCOPES = ["https://www.googleapis.com/auth/youtube"]


def upload_video(video_path: Path, plan: VideoPlan, settings: Settings, playlist_id: str = "") -> str:
    client_secrets = ROOT / settings.youtube_client_secrets
    token_file = ROOT / settings.youtube_token_file
    if not token_file.exists():
        raise FileNotFoundError(f"token.json bulunamadi: {token_file}")

    creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            token_file.write_text(creds.to_json(), encoding="utf-8")
        else:
            raise RuntimeError("YouTube credentials gecersiz, token.json'u yenileyin.")

    youtube = build("youtube", "v3", credentials=creds)
    body = {
        "snippet": {
            "title": plan.title[:100],
            "description": plan.description,
            "tags": plan.tags,
            "categoryId": "27",
        },
        "status": {"privacyStatus": settings.default_privacy_status},
    }
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=MediaFileUpload(str(video_path), chunksize=-1, resumable=True),
    )
    response = request.execute()
    video_id = response["id"]

    if playlist_id:
        youtube.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {"kind": "youtube#video", "videoId": video_id},
                }
            },
        ).execute()

    return f"https://www.youtube.com/watch?v={video_id}"
