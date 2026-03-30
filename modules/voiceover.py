# modules/voiceover.py
# MrBeast style — ৩টি আলাদা ভাষার audio track তৈরি করে
# ElevenLabs (ভালো quality) → না থাকলে gTTS (ফ্রি) fallback

import requests
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    ELEVENLABS_API_KEY,
    ELEVENLABS_VOICE_ID_BN,
    ELEVENLABS_VOICE_ID_EN,
    ELEVENLABS_VOICE_ID_HI,
)

OUTPUT_DIR = "temp/audio"

LANGUAGE_CONFIG = {
    "bn": {
        "field":     "narration",
        "voice_id":  ELEVENLABS_VOICE_ID_BN,
        "gtts_lang": "bn",
        "label":     "বাংলা",
        "yt_name":   "Bengali",
    },
    "en": {
        "field":     "translation_english",
        "voice_id":  ELEVENLABS_VOICE_ID_EN,
        "gtts_lang": "en",
        "label":     "English",
        "yt_name":   "English",
    },
    "hi": {
        "field":     "translation_hindi",
        "voice_id":  ELEVENLABS_VOICE_ID_HI,
        "gtts_lang": "hi",
        "label":     "हिंदी",
        "yt_name":   "Hindi",
    },
}


# ── ElevenLabs TTS ────────────────────────────────────────────

def _elevenlabs_tts(text: str, voice_id: str, filepath: str) -> bool:
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
        else:
            print(f"    ⚠️ ElevenLabs error {response.status_code}")
            return False
    except Exception as e:
        print(f"    ⚠️ ElevenLabs exception: {e}")
        return False


# ── gTTS Fallback ─────────────────────────────────────────────

def _gtts_tts(text: str, lang: str, filepath: str) -> bool:
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(filepath)
        return True
    except Exception as e:
        print(f"    ⚠️ gTTS error: {e}")
        return False


# ── Silence Fallback ──────────────────────────────────────────

def _silence(filename: str, duration: int = 5) -> str:
    from pydub import AudioSegment
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(OUTPUT_DIR, filename)
    AudioSegment.silent(duration=duration * 1000).export(filepath, format="mp3")
    return filepath


# ── Single voiceover ──────────────────────────────────────────

def generate_voiceover_lang(text: str, lang_code: str, filename: str) -> str:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(OUTPUT_DIR, filename)
    cfg = LANGUAGE_CONFIG[lang_code]

    print(f"    🎤 {cfg['label']} voiceover: {filename}")

    if _elevenlabs_tts(text, cfg["voice_id"], filepath):
        print(f"    ✅ ElevenLabs দিয়ে তৈরি")
        return filepath

    print(f"    ↩️  gTTS fallback চেষ্টা করছে...")
    if _gtts_tts(text, cfg["gtts_lang"], filepath):
        print(f"    ✅ gTTS দিয়ে তৈরি")
        return filepath

    print(f"    ⚠️  Silence fallback")
    return _silence(filename)


# ── All scenes, all languages ─────────────────────────────────

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
    print(f"\n🎤 {len(scenes)}টি scene x ৩ ভাষা = {len(scenes)*3}টি voiceover তৈরি হচ্ছে...")
    print("   (MrBeast style — দর্শক YouTube-এ ভাষা বেছে নেবে)\n")

    all_paths = {"bn": [], "en": [], "hi": []}

    for scene in scenes:
        scene_num = scene["scene_number"]
        print(f"  Scene {scene_num}:")

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


# ── Merge scenes into one full audio per language ─────────────

def merge_language_audio(audio_paths: list, lang_code: str) -> str:
    """একটা ভাষার সব scene audio জোড়া লাগিয়ে একটা ফাইল বানায়।"""
    from pydub import AudioSegment

    print(f"  🔗 {LANGUAGE_CONFIG[lang_code]['label']} audio merge হচ্ছে...")
    combined = AudioSegment.empty()

    for path in audio_paths:
        if os.path.exists(path):
            combined += AudioSegment.from_mp3(path)
        else:
            combined += AudioSegment.silent(duration=3000)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, f"full_track_{lang_code}.mp3")
    combined.export(out_path, format="mp3")
    print(f"  ✅ Merged: {out_path} ({len(combined)/1000:.1f}s)")
    return out_path


def merge_all_language_tracks(all_paths: dict) -> dict:
    """
    ৩ ভাষার full audio track বানায়।
    YouTube uploader এটা ব্যবহার করবে।

    Returns:
    {
        "bn": "temp/audio/full_track_bn.mp3",
        "en": "temp/audio/full_track_en.mp3",
        "hi": "temp/audio/full_track_hi.mp3",
    }
    """
    print(f"\n🔗 Full language tracks merge হচ্ছে...")
    merged = {}
    for lang_code, paths in all_paths.items():
        merged[lang_code] = merge_language_audio(paths, lang_code)
    return merged


# ── Helper ───────────────────────────────────────────────────

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
