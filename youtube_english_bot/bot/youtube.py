from pathlib import Path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from .config import ROOT, Settings
from .models import VideoPlan

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def upload_video(video_path: Path, plan: VideoPlan, settings: Settings) -> str:
    client_secrets = ROOT / settings.youtube_client_secrets
    token_file = ROOT / settings.youtube_token_file
    if not client_secrets.exists():
        raise FileNotFoundError(
            f"YouTube OAuth dosyasi bulunamadi: {client_secrets}. Google Cloud'dan indirip bu adla kaydedin."
        )

    creds = None
    if token_file.exists():
        creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(str(client_secrets), SCOPES)
        creds = flow.run_local_server(port=0)
        token_file.write_text(creds.to_json(), encoding="utf-8")

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
    return f"https://www.youtube.com/watch?v={response['id']}"
