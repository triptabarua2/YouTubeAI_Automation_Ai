# modules/voiceover.py
# MrBeast style — ৩টি আলাদা ভাষার audio track তৈরি করে
#
# Fallback ক্রম:
#   ১. ElevenLabs      (সেরা মান, মাসে ১০,০০০ chars ফ্রি)
#   ২. Google Cloud TTS (ElevenLabs শেষ হলে, মাসে ১০ লাখ chars ফ্রি!)
#   ৩. gTTS            (সম্পূর্ণ ফ্রি, unlimited, একটু robotic)
#   ৪. Silence         (সব fail হলে নীরব audio)

import requests
import os
import sys
import base64
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    ELEVENLABS_API_KEY,
    ELEVENLABS_VOICE_ID_BN,
    ELEVENLABS_VOICE_ID_EN,
    ELEVENLABS_VOICE_ID_HI,
    GOOGLE_CLOUD_TTS_API_KEY,
)

OUTPUT_DIR = "temp/audio"

LANGUAGE_CONFIG = {
    "bn": {
        "field":        "narration",
        "voice_id":     ELEVENLABS_VOICE_ID_BN,
        "gtts_lang":    "bn",
        "label":        "বাংলা",
        "yt_name":      "Bengali",
        # Google Cloud TTS voice
        "gcloud_lang":  "bn-BD",
        "gcloud_voice": "bn-BD-Standard-A",
    },
    "en": {
        "field":        "translation_english",
        "voice_id":     ELEVENLABS_VOICE_ID_EN,
        "gtts_lang":    "en",
        "label":        "English",
        "yt_name":      "English",
        "gcloud_lang":  "en-US",
        "gcloud_voice": "en-US-Neural2-D",
    },
    "hi": {
        "field":        "translation_hindi",
        "voice_id":     ELEVENLABS_VOICE_ID_HI,
        "gtts_lang":    "hi",
        "label":        "हिंदी",
        "yt_name":      "Hindi",
        "gcloud_lang":  "hi-IN",
        "gcloud_voice": "hi-IN-Neural2-A",
    },
}


# ══════════════════════════════════════════════════════════════
#  ১. ElevenLabs TTS
# ══════════════════════════════════════════════════════════════

def _elevenlabs_tts(text: str, voice_id: str, filepath: str) -> bool:
    """ElevenLabs — সেরা মান। limit শেষ হলে False return করে।"""
    if not ELEVENLABS_API_KEY or ELEVENLABS_API_KEY == "YOUR_ELEVENLABS_API_KEY":
        return False
    if not voice_id or voice_id.startswith("YOUR_"):
        return False

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"}
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.6,
            "similarity_boost": 0.8,
            "style": 0.3,
            "use_speaker_boost": True
        }
    }
    try:
        response = requests.post(url, json=data, headers=headers, timeout=60)
        if response.status_code == 200:
            with open(filepath, "wb") as f:
                f.write(response.content)
            return True
        elif response.status_code == 429:
            print(f"    ⚠️ ElevenLabs limit শেষ! Google Cloud TTS-এ যাচ্ছে...")
            return False
        else:
            print(f"    ⚠️ ElevenLabs error {response.status_code}")
            return False
    except Exception as e:
        print(f"    ⚠️ ElevenLabs exception: {e}")
        return False


# ══════════════════════════════════════════════════════════════
#  ২. Google Cloud TTS (Fallback ১)
# ══════════════════════════════════════════════════════════════

def _google_cloud_tts(text: str, lang_code: str, filepath: str) -> bool:
    """
    Google Cloud TTS — মাসে ১০ লাখ chars ফ্রি!
    ElevenLabs-এর কাছাকাছি মান।
    """
    if not GOOGLE_CLOUD_TTS_API_KEY or GOOGLE_CLOUD_TTS_API_KEY == "YOUR_GOOGLE_CLOUD_TTS_API_KEY":
        return False

    cfg = LANGUAGE_CONFIG[lang_code]
    url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={GOOGLE_CLOUD_TTS_API_KEY}"

    body = {
        "input": {"text": text},
        "voice": {
            "languageCode": cfg["gcloud_lang"],
            "name":         cfg["gcloud_voice"],
            "ssmlGender":   "NEUTRAL"
        },
        "audioConfig": {
            "audioEncoding":   "MP3",
            "speakingRate":    1.0,
            "pitch":           0.0,
            "volumeGainDb":    0.0,
        }
    }

    try:
        response = requests.post(url, json=body, timeout=30)
        if response.status_code == 200:
            audio_content = response.json().get("audioContent", "")
            if audio_content:
                with open(filepath, "wb") as f:
                    f.write(base64.b64decode(audio_content))
                return True
            return False
        elif response.status_code == 429:
            print(f"    ⚠️ Google Cloud TTS limit! gTTS-এ যাচ্ছে...")
            return False
        else:
            print(f"    ⚠️ Google Cloud TTS error {response.status_code}: {response.text[:100]}")
            return False
    except Exception as e:
        print(f"    ⚠️ Google Cloud TTS exception: {e}")
        return False


# ══════════════════════════════════════════════════════════════
#  ৩. gTTS Fallback (Fallback ২)
# ══════════════════════════════════════════════════════════════

def _gtts_tts(text: str, lang: str, filepath: str) -> bool:
    """gTTS — সম্পূর্ণ ফ্রি, unlimited। একটু robotic কিন্তু কাজ চলে।"""
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(filepath)
        return True
    except Exception as e:
        print(f"    ⚠️ gTTS error: {e}")
        return False


# ══════════════════════════════════════════════════════════════
#  ৪. Silence (সব fail হলে)
# ══════════════════════════════════════════════════════════════

def _silence(filename: str, duration: int = 5) -> str:
    from pydub import AudioSegment
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(OUTPUT_DIR, filename)
    AudioSegment.silent(duration=duration * 1000).export(filepath, format="mp3")
    return filepath


# ══════════════════════════════════════════════════════════════
#  Main: Single voiceover
# ══════════════════════════════════════════════════════════════

def generate_voiceover_lang(text: str, lang_code: str, filename: str) -> str:
    """
    একটা ভাষার voiceover বানায়।
    ক্রম: ElevenLabs → Google Cloud TTS → gTTS → Silence
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(OUTPUT_DIR, filename)
    cfg = LANGUAGE_CONFIG[lang_code]

    print(f"    🎤 {cfg['label']}: {filename}")

    # ১. ElevenLabs
    if _elevenlabs_tts(text, cfg["voice_id"], filepath):
        print(f"    ✅ ElevenLabs ✓")
        return filepath

    # ২. Google Cloud TTS
    print(f"    ↩️  Google Cloud TTS চেষ্টা করছে...")
    if _google_cloud_tts(text, lang_code, filepath):
        print(f"    ✅ Google Cloud TTS ✓")
        return filepath

    # ৩. gTTS
    print(f"    ↩️  gTTS চেষ্টা করছে...")
    if _gtts_tts(text, cfg["gtts_lang"], filepath):
        print(f"    ✅ gTTS ✓")
        return filepath

    # ৪. Silence
    print(f"    ⚠️  Silence fallback")
    return _silence(filename)


# ══════════════════════════════════════════════════════════════
#  All scenes × all languages
# ══════════════════════════════════════════════════════════════

def generate_all_voiceovers(scenes: list) -> dict:
    """
    সব scene-এর ৩ ভাষার voiceover বানায়।

    Returns:
    {
        "bn": ["temp/audio/bn_scene_01.mp3", ...],
        "en": ["temp/audio/en_scene_01.mp3", ...],
        "hi": ["temp/audio/hi_scene_01.mp3", ...],
    }
    """
    total = len(scenes) * 3
    print(f"\n🎤 {len(scenes)} scene × ৩ ভাষা = {total}টি voiceover তৈরি হচ্ছে...")
    print("   Fallback ক্রম: ElevenLabs → Google Cloud TTS → gTTS\n")

    all_paths = {"bn": [], "en": [], "hi": []}

    for scene in scenes:
        scene_num = scene["scene_number"]
        print(f"  📍 Scene {scene_num}:")

        for lang_code, cfg in LANGUAGE_CONFIG.items():
            text     = scene.get(cfg["field"], "")
            filename = f"{lang_code}_scene_{scene_num:02d}.mp3"

            if not text.strip():
                print(f"    ⚠️ {cfg['label']} text নেই — silence")
                path = _silence(filename)
            else:
                path = generate_voiceover_lang(text, lang_code, filename)

            all_paths[lang_code].append(path)

    print(f"\n✅ সব voiceover তৈরি!")
    print(f"   বাংলা  : {len(all_paths['bn'])}টি")
    print(f"   English: {len(all_paths['en'])}টি")
    print(f"   हिंदी  : {len(all_paths['hi'])}টি")
    return all_paths


# ══════════════════════════════════════════════════════════════
#  Merge all scenes → one full track per language
# ══════════════════════════════════════════════════════════════

def merge_language_audio(audio_paths: list, lang_code: str) -> str:
    """একটা ভাষার সব scene audio জোড়া লাগিয়ে একটা ফাইল বানায়।"""
    from pydub import AudioSegment

    print(f"  🔗 {LANGUAGE_CONFIG[lang_code]['label']} merge হচ্ছে...")
    combined = AudioSegment.empty()

    for path in audio_paths:
        if os.path.exists(path):
            combined += AudioSegment.from_mp3(path)
        else:
            combined += AudioSegment.silent(duration=3000)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, f"full_track_{lang_code}.mp3")
    combined.export(out_path, format="mp3")
    print(f"  ✅ {out_path} ({len(combined)/1000:.1f}s)")
    return out_path


def merge_all_language_tracks(all_paths: dict) -> dict:
    """
    ৩ ভাষার full audio track বানায়।
    Returns: {"bn": "path", "en": "path", "hi": "path"}
    """
    print(f"\n🔗 Full language tracks merge হচ্ছে...")
    return {lang: merge_language_audio(paths, lang) for lang, paths in all_paths.items()}


# ══════════════════════════════════════════════════════════════
#  Helper
# ══════════════════════════════════════════════════════════════

def get_available_voices():
    """ElevenLabs-এ available voices দেখায়"""
    if not ELEVENLABS_API_KEY or ELEVENLABS_API_KEY == "YOUR_ELEVENLABS_API_KEY":
        print("⚠️ ElevenLabs API key নেই")
        return
    url = "https://api.elevenlabs.io/v1/voices"
    headers = {"xi-api-key": ELEVENLABS_API_KEY}
    try:
        response = requests.get(url, headers=headers)
        voices = response.json().get("voices", [])
        print("\n📢 Available Voices:")
        for v in voices[:15]:
            print(f"  - {v['name']}: {v['voice_id']}")
    except Exception as e:
        print(f"Error: {e}")


def test_google_cloud_tts():
    """Google Cloud TTS ঠিকমতো কাজ করছে কিনা test করে"""
    print("\n🧪 Google Cloud TTS test হচ্ছে...")
    test_cases = [
        ("bn", "হ্যালো, এটা একটা পরীক্ষা।"),
        ("en", "Hello, this is a test."),
        ("hi", "नमस्ते, यह एक परीक्षण है।"),
    ]
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for lang, text in test_cases:
        filepath = os.path.join(OUTPUT_DIR, f"test_{lang}.mp3")
        ok = _google_cloud_tts(text, lang, filepath)
        status = "✅" if ok else "❌"
        print(f"  {status} {LANGUAGE_CONFIG[lang]['label']}: {filepath if ok else 'failed'}")
