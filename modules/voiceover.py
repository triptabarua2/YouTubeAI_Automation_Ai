# modules/voiceover.py
# MrBeast style — ৩টি audio track (বাংলা, English, হিন্দি)
# Fallback: ElevenLabs → Google Cloud TTS → gTTS → Silence

import requests, os, sys, base64
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID_BN,
    ELEVENLABS_VOICE_ID_EN, ELEVENLABS_VOICE_ID_HI,
    GOOGLE_CLOUD_TTS_API_KEY,
)

DEFAULT_OUTPUT_DIR = "temp/audio"

LANGUAGE_CONFIG = {
    "bn": {
        "field": "narration", "voice_id": ELEVENLABS_VOICE_ID_BN,
        "gtts_lang": "bn", "label": "বাংলা", "yt_name": "Bengali",
        "gcloud_lang": "bn-BD", "gcloud_voice": "bn-BD-Standard-A",
    },
    "en": {
        "field": "translation_english", "voice_id": ELEVENLABS_VOICE_ID_EN,
        "gtts_lang": "en", "label": "English", "yt_name": "English",
        "gcloud_lang": "en-US", "gcloud_voice": "en-US-Neural2-D",
    },
    "hi": {
        "field": "translation_hindi", "voice_id": ELEVENLABS_VOICE_ID_HI,
        "gtts_lang": "hi", "label": "हिंदी", "yt_name": "Hindi",
        "gcloud_lang": "hi-IN", "gcloud_voice": "hi-IN-Neural2-A",
    },
}


def _elevenlabs_tts(text, voice_id, filepath):
    if not ELEVENLABS_API_KEY or ELEVENLABS_API_KEY == "YOUR_ELEVENLABS_API_KEY": return False
    if not voice_id or voice_id.startswith("YOUR_"): return False
    try:
        r = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            headers={"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"},
            json={"text": text, "model_id": "eleven_multilingual_v2",
                  "voice_settings": {"stability": 0.6, "similarity_boost": 0.8,
                                     "style": 0.3, "use_speaker_boost": True}},
            timeout=60
        )
        if r.status_code == 200:
            open(filepath, "wb").write(r.content); return True
        if r.status_code == 429: print("    ⚠️ ElevenLabs limit শেষ!")
        return False
    except Exception as e:
        print(f"    ⚠️ ElevenLabs: {e}"); return False


def _google_cloud_tts(text, lang_code, filepath):
    if not GOOGLE_CLOUD_TTS_API_KEY or GOOGLE_CLOUD_TTS_API_KEY == "YOUR_GOOGLE_CLOUD_TTS_API_KEY": return False
    cfg = LANGUAGE_CONFIG[lang_code]
    try:
        r = requests.post(
            f"https://texttospeech.googleapis.com/v1/text:synthesize?key={GOOGLE_CLOUD_TTS_API_KEY}",
            json={"input": {"text": text},
                  "voice": {"languageCode": cfg["gcloud_lang"], "name": cfg["gcloud_voice"]},
                  "audioConfig": {"audioEncoding": "MP3", "speakingRate": 1.0}},
            timeout=30
        )
        if r.status_code == 200:
            audio = r.json().get("audioContent", "")
            if audio:
                open(filepath, "wb").write(base64.b64decode(audio)); return True
        return False
    except Exception as e:
        print(f"    ⚠️ Google Cloud TTS: {e}"); return False


def _gtts_tts(text, lang, filepath):
    try:
        from gtts import gTTS
        gTTS(text=text, lang=lang, slow=False).save(filepath); return True
    except Exception as e:
        print(f"    ⚠️ gTTS: {e}"); return False


def _silence(filename, duration=5, output_dir=None):
    from pydub import AudioSegment
    out = output_dir or DEFAULT_OUTPUT_DIR
    os.makedirs(out, exist_ok=True)
    fp  = os.path.join(out, filename)
    AudioSegment.silent(duration=duration * 1000).export(fp, format="mp3")
    return fp


def generate_voiceover_lang(text, lang_code, filename, output_dir=None):
    out = output_dir or DEFAULT_OUTPUT_DIR
    os.makedirs(out, exist_ok=True)
    filepath = os.path.join(out, filename)
    cfg = LANGUAGE_CONFIG[lang_code]
    print(f"    🎤 {cfg['label']}: {filename}")

    if _elevenlabs_tts(text, cfg["voice_id"], filepath):
        print("    ✅ ElevenLabs ✓"); return filepath
    print("    ↩️  Google Cloud TTS...")
    if _google_cloud_tts(text, lang_code, filepath):
        print("    ✅ Google Cloud TTS ✓"); return filepath
    print("    ↩️  gTTS...")
    if _gtts_tts(text, cfg["gtts_lang"], filepath):
        print("    ✅ gTTS ✓"); return filepath
    print("    ⚠️  Silence fallback")
    return _silence(filename, output_dir=out)


def generate_all_voiceovers(scenes, temp_dir=None):
    out = os.path.join(temp_dir, "audio") if temp_dir else DEFAULT_OUTPUT_DIR
    print(f"\n🎤 {len(scenes)} scene × ৩ ভাষা = {len(scenes)*3}টি voiceover...")
    all_paths = {"bn": [], "en": [], "hi": []}
    for scene in scenes:
        n = scene["scene_number"]
        print(f"  Scene {n}:")
        for lang_code, cfg in LANGUAGE_CONFIG.items():
            text = scene.get(cfg["field"], "")
            fn   = f"{lang_code}_scene_{n:02d}.mp3"
            path = generate_voiceover_lang(text, lang_code, fn, output_dir=out) \
                   if text.strip() else _silence(fn, output_dir=out)
            all_paths[lang_code].append(path)
    print(f"\n✅ সব voiceover তৈরি!")
    return all_paths


def merge_language_audio(audio_paths, lang_code, output_dir=None):
    from pydub import AudioSegment
    out = output_dir or DEFAULT_OUTPUT_DIR
    os.makedirs(out, exist_ok=True)
    combined = AudioSegment.empty()
    for p in audio_paths:
        combined += AudioSegment.from_mp3(p) if os.path.exists(p) else AudioSegment.silent(3000)
    out_path = os.path.join(out, f"full_track_{lang_code}.mp3")
    combined.export(out_path, format="mp3")
    print(f"  ✅ {LANGUAGE_CONFIG[lang_code]['label']} merged ({len(combined)/1000:.1f}s)")
    return out_path


def merge_all_language_tracks(all_paths, temp_dir=None):
    out = os.path.join(temp_dir, "audio") if temp_dir else DEFAULT_OUTPUT_DIR
    print(f"\n🔗 Language tracks merge হচ্ছে...")
    return {lang: merge_language_audio(paths, lang, output_dir=out)
            for lang, paths in all_paths.items()}
