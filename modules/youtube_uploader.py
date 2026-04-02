# modules/youtube_uploader.py
# Multi-channel support — প্রতিটা channel-এর আলাদা credentials

import os, sys, pickle, time
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
]
LANG_NAMES = {"bn": "Bengali", "en": "English", "hi": "Hindi"}


def get_youtube_service(client_secret: str, token_file: str):
    creds = None
    if os.path.exists(token_file):
        with open(token_file, "rb") as f:
            creds = pickle.load(f)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow  = InstalledAppFlow.from_client_secrets_file(client_secret, SCOPES)
            try:
                # Try to run local server (works if browser is available)
                creds = flow.run_local_server(port=0, open_browser=False)
            except Exception:
                # Fallback for environments without browser access
                print("\n⚠️  Browser open failed. Please use the following link to authorize:")
                creds = flow.run_console()
        with open(token_file, "wb") as f:
            pickle.dump(creds, f)
    return build("youtube", "v3", credentials=creds)


def upload_video(video_path, thumbnail_path, script_data,
                 audio_tracks=None,
                 client_secret="client_secret.json",
                 token_file="youtube_token.pickle",
                 category_id="27",
                 language="bn") -> str:

    print(f"\n📤 YouTube upload হচ্ছে...")
    youtube = get_youtube_service(client_secret, token_file)

    body = {
        "snippet": {
            "title":                script_data["title"],
            "description":          script_data["description"],
            "tags":                 script_data["tags"],
            "categoryId":           category_id,
            "defaultLanguage":      language,
            "defaultAudioLanguage": language,
        },
        "status": {"privacyStatus": "private", "selfDeclaredMadeForKids": False}
    }

    media    = MediaFileUpload(video_path, chunksize=1024*1024, resumable=True, mimetype="video/mp4")
    request  = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status: print(f"  📤 {int(status.progress()*100)}%")

    video_id = response["id"]
    print(f"  ✅ Upload সম্পন্ন! ID: {video_id}")

    if thumbnail_path and os.path.exists(thumbnail_path):
        try:
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path)
            ).execute()
            print("  ✅ Thumbnail set")
        except Exception as e:
            print(f"  ⚠️ Thumbnail: {e}")

    if audio_tracks:
        print(f"\n🎧 ৩টি audio track upload হচ্ছে...")
        for lang_code, track_path in audio_tracks.items():
            if not track_path or not os.path.exists(track_path):
                continue
            lang_name = LANG_NAMES.get(lang_code, lang_code)
            try:
                # req = youtube.videoAudioTracks().insert(
                #     part="snippet", videoId=video_id,
                #     body={"snippet": {"language": lang_code, "displayName": lang_name,
                #                       "isDefault": (lang_code == language)}},
                #     media_body=MediaFileUpload(track_path, resumable=True, mimetype="audio/mpeg")
                # )
                # resp = None
                # while resp is None:
                #     st, resp = req.next_chunk()
                # print(f"  ✅ {lang_name} track যোগ হয়েছে!")
                print(f"  ⚠️ {lang_name} track upload skipped (API not publicly available)")
                time.sleep(2)
            except Exception as e:
                print(f"  ⚠️ {lang_name} track error: {e}")

    url = f"https://youtube.com/watch?v={video_id}"
    print(f"\n🎉 Live: {url}")
    print("⚠️  Private আছে। দেখে Public করুন।")
    return url


def make_video_public(video_id, client_secret="client_secret.json", token_file="youtube_token.pickle"):
    youtube = get_youtube_service(client_secret, token_file)
    youtube.videos().update(
        part="status",
        body={"id": video_id, "status": {"privacyStatus": "public"}}
    ).execute()
    print("✅ Video public হয়েছে!")
