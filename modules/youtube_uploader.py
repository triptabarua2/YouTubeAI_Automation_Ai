# modules/youtube_uploader.py
# YouTube Data API দিয়ে video + ৩টি audio track upload করে
# MrBeast style — দর্শক YouTube-এ ভাষা বেছে নেবে

import os
import sys
import pickle
import time
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import YOUTUBE_CLIENT_SECRET_FILE, VIDEO_CATEGORY_ID, CHANNEL_LANGUAGE

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
]
TOKEN_FILE = "youtube_token.pickle"

# YouTube audio track language mapping
LANG_NAMES = {
    "bn": "Bengali",
    "en": "English",
    "hi": "Hindi",
}


def get_youtube_service():
    """YouTube API connection তৈরি করে"""
    creds = None

    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                YOUTUBE_CLIENT_SECRET_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)

    return build("youtube", "v3", credentials=creds)


def upload_video(video_path: str, thumbnail_path: str, script_data: dict,
                 audio_tracks: dict = None) -> str:
    """
    Video YouTube-এ upload করে।
    audio_tracks = {"bn": "path.mp3", "en": "path.mp3", "hi": "path.mp3"}
    Returns: Video URL
    """
    print(f"\n📤 YouTube-এ upload হচ্ছে...")

    youtube = get_youtube_service()

    # Video metadata
    body = {
        "snippet": {
            "title":                script_data["title"],
            "description":          script_data["description"],
            "tags":                 script_data["tags"],
            "categoryId":           VIDEO_CATEGORY_ID,
            "defaultLanguage":      CHANNEL_LANGUAGE,
            "defaultAudioLanguage": CHANNEL_LANGUAGE,
        },
        "status": {
            "privacyStatus":           "private",
            "selfDeclaredMadeForKids": False,
        }
    }

    # ── Video upload ──────────────────────────────────────────
    media = MediaFileUpload(
        video_path,
        chunksize=1024 * 1024,
        resumable=True,
        mimetype="video/mp4"
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            progress = int(status.progress() * 100)
            print(f"  📤 Upload: {progress}%")

    video_id = response["id"]
    print(f"  ✅ Video upload সম্পন্ন! ID: {video_id}")

    # ── Thumbnail ─────────────────────────────────────────────
    if thumbnail_path and os.path.exists(thumbnail_path):
        try:
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path)
            ).execute()
            print(f"  ✅ Thumbnail set হয়েছে")
        except Exception as e:
            print(f"  ⚠️ Thumbnail error: {e}")

    # ── Audio Tracks (MrBeast style) ──────────────────────────
    if audio_tracks:
        print(f"\n🎧 ৩টি ভাষার audio track upload হচ্ছে...")
        _upload_audio_tracks(youtube, video_id, audio_tracks)
    else:
        print(f"\n⚠️ Audio tracks নেই — শুধু video upload হয়েছে")

    video_url = f"https://youtube.com/watch?v={video_id}"
    print(f"\n🎉 Video live: {video_url}")
    print(f"⚠️  এখন private আছে। দেখে approve করলে Public করুন।")
    return video_url


def _upload_audio_tracks(youtube, video_id: str, audio_tracks: dict):
    """
    ৩টি ভাষার audio track আলাদাভাবে YouTube-এ যোগ করে।
    দর্শক YouTube player-এ ভাষা বেছে নিতে পারবে।
    """
    # বাংলা default track (video-র সাথে আছে)
    # English ও Hindi আলাদাভাবে যোগ করতে হবে

    for lang_code, track_path in audio_tracks.items():
        if not track_path or not os.path.exists(track_path):
            print(f"  ⚠️ {LANG_NAMES.get(lang_code, lang_code)} track নেই, skip")
            continue

        lang_name = LANG_NAMES.get(lang_code, lang_code)
        print(f"  🎧 {lang_name} track upload হচ্ছে...")

        try:
            media = MediaFileUpload(
                track_path,
                resumable=True,
                mimetype="audio/mpeg"
            )

            request = youtube.videoAudioTracks().insert(
                part="snippet",
                videoId=video_id,
                body={
                    "snippet": {
                        "language":    lang_code,
                        "displayName": lang_name,
                        "isDefault":   (lang_code == CHANNEL_LANGUAGE),
                    }
                },
                media_body=media
            )

            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    print(f"    📤 {lang_name}: {int(status.progress()*100)}%")

            print(f"  ✅ {lang_name} track যোগ হয়েছে!")
            time.sleep(2)  # Rate limit এড়াতে

        except Exception as e:
            print(f"  ⚠️ {lang_name} track error: {e}")
            print(f"     (Note: YouTube audio track API কিছু channel-এ সীমিত)")


def make_video_public(video_id: str):
    """Video public করে"""
    youtube = get_youtube_service()
    youtube.videos().update(
        part="status",
        body={
            "id":     video_id,
            "status": {"privacyStatus": "public"}
        }
    ).execute()
    print(f"✅ Video public হয়েছে!")
