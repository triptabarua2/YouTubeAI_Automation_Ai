# ============================================================
#  config.py — সব API Key এবং ৩টি Channel Settings
# ============================================================

import os
from dotenv import load_dotenv

# .env ফাইল থেকে environment variables লোড করা
load_dotenv()

# ✅ Telegram Bot — মোবাইলে notification (ফ্রি)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID")

# ✅ Google Gemini — script লেখার জন্য (ফ্রি)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# ✅ ElevenLabs — voiceover (মাসে ১০,০০০ chars ফ্রি)
ELEVENLABS_API_KEY     = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID_BN = os.getenv("ELEVENLABS_VOICE_ID_BN", "YOUR_BENGALI_VOICE_ID")
ELEVENLABS_VOICE_ID_EN = os.getenv("ELEVENLABS_VOICE_ID_EN", "YOUR_ENGLISH_VOICE_ID")
ELEVENLABS_VOICE_ID_HI = os.getenv("ELEVENLABS_VOICE_ID_HI", "DpnM70iDHNHZ0Mguv6GJ")
ELEVENLABS_VOICE_ID    = ELEVENLABS_VOICE_ID_HI  # Set Hindi as default since BN is unavailable

# ✅ Google Cloud TTS — ElevenLabs শেষ হলে fallback (মাসে ১০ লাখ chars ফ্রি)
GOOGLE_CLOUD_TTS_API_KEY = os.getenv("GOOGLE_CLOUD_TTS_API_KEY")

# ✅ Pixabay — background music (ফ্রি)
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")

# ✅ YouTube client secret — ৩টা channel-এর জন্য আলাদা file
# console.cloud.google.com থেকে প্রতিটা channel-এর OAuth credentials ডাউনলোড করুন
# ============================================================

# ============================================================
#  ৩টি Channel-এর Settings
# ============================================================
CHANNELS = {

    "channel_1": {
        "name":              "আমার বাংলা চ্যানেল ১",          # channel-এর নাম
        "topic":             "funny",                          # channel-এর বিষয়
        "topic_description": "বাংলাদেশের মজার ও হাসির ঘটনা, viral memes, comedy animation",
        "style":             "funny, relatable, Bangladeshi humor",
        "upload_time":       "09:00",                         # সকাল ৯টায়
        "client_secret":     "client_secret_channel1.json",   # YouTube OAuth file
        "token_file":        "token_channel1.pickle",
        "category_id":       "23",                            # 23 = Comedy
        "language":          "bn",
    },

    "channel_2": {
        "name":              "আমার বাংলা চ্যানেল ২",
        "topic":             "educational",
        "topic_description": "বাংলাদেশ ও বিশ্বের অজানা তথ্য, ইতিহাস, বিজ্ঞান, শিক্ষামূলক animation",
        "style":             "educational, informative, engaging, suitable for all ages",
        "upload_time":       "13:00",                         # দুপুর ১টায়
        "client_secret":     "client_secret_channel2.json",
        "token_file":        "token_channel2.pickle",
        "category_id":       "27",                            # 27 = Education
        "language":          "bn",
    },

    "channel_3": {
        "name":              "আমার বাংলা চ্যানেল ৩",
        "topic":             "storytelling",
        "topic_description": "বাংলাদেশের রহস্য, ভূতের গল্প, রোমাঞ্চকর কাহিনী, mystery animation",
        "style":             "mysterious, thrilling, dramatic, suspenseful",
        "upload_time":       "20:00",                         # রাত ৮টায়
        "client_secret":     "client_secret_channel3.json",
        "token_file":        "token_channel3.pickle",
        "category_id":       "24",                            # 24 = Entertainment
        "language":          "bn",
    },

}

# ============================================================
#  Global Video Settings (সব channel-এ একই)
# ============================================================
SCENES_PER_VIDEO       = 8
FPS                    = 24
RESOLUTION             = (1920, 1080)
VIDEO_DURATION_SECONDS = 180
# Font Path
FONT_PATH = os.path.join("assets", "Kalpurush.ttf")
