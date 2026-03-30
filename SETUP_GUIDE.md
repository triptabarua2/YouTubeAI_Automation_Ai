# 🎬 YouTube AI Full Automation — সেটআপ গাইড

## এই system কী করবে?
```
আপনি কিছু না করলেও প্রতিদিন:
Topic বাছাই → Script লেখা → AI Image বানানো → 
Multi-language Voiceover দেওয়া → Video Edit → YouTube Upload (Multi-audio tracks সহ)
```

---

## ধাপ ১ — Python ইনস্টল করুন
👉 https://python.org/downloads (3.10 বা উপরে)

---

## ধাপ ২ — Libraries ইনস্টল করুন
```bash
pip install -r requirements.txt
```

---

## ধাপ ৩ — API Keys সংগ্রহ করুন

### A) Google API Key (Gemini — Script লেখার জন্য)
1.  https://aistudio.google.com/app/apikey যান
2.  একটি নতুন API Key তৈরি করুন এবং কপি করুন।
3.  `config.py` তে `GOOGLE_API_KEY = "..."` এখানে বসান।

### B) ElevenLabs API Key (Voiceover — বাংলা, English, হিন্দি voice)
1.  https://elevenlabs.io যান
2.  Free Sign Up করুন।
3.  Profile → API Key → Copy করুন।
4.  Voices → Voice Library থেকে আপনার পছন্দের বাংলা, English এবং হিন্দি ভয়েস বেছে নিন এবং তাদের Voice ID কপি করুন।
5.  `config.py` তে `ELEVENLABS_API_KEY`, `ELEVENLABS_VOICE_ID_BN`, `ELEVENLABS_VOICE_ID_EN`, `ELEVENLABS_VOICE_ID_HI` এখানে বসান।
    *   যদি ElevenLabs API Key না থাকে বা ব্যবহার করতে না চান, তাহলে gTTS (Google Text-to-Speech) স্বয়ংক্রিয়ভাবে ফলব্যাক হিসেবে কাজ করবে।

### C) YouTube API (Upload করার জন্য)
1.  https://console.cloud.google.com যান
2.  একটি নতুন Project বানান: "YouTubeAI"
3.  APIs & Services → Enable → "YouTube Data API v3" সার্চ করে Enable করুন।
4.  Credentials → OAuth 2.0 Client ID → Desktop App সিলেক্ট করুন।
5.  JSON ফাইলটি ডাউনলোড করুন এবং `client_secret.json` নামে এই প্রজেক্ট ফোল্ডারে রাখুন।

---

## ধাপ ৪ — Music যোগ করুন (Optional)
`music/` folder-এ যেকোনো royalty-free .mp3 ফাইল রাখুন।
ফ্রি music পাবেন: https://pixabay.com/music

---

## ধাপ ৫ — Run করুন!

### একটি video বানানো (topic নিজে দিয়ে):
```bash
python main.py --topic "বাংলাদেশের সেরা ১০টি রহস্য"
```

### AI নিজে topic বাছুক:
```bash
python main.py
```

### Video বানিয়ে সাথে সাথে upload করা:
```bash
python main.py --auto-upload
```

### প্রতিদিন automatic (schedule mode):
```bash
python main.py --schedule
```
> এটা চালিয়ে রাখলে `config.py` তে দেওয়া সময়ে প্রতিদিন video বানিয়ে upload করবে!

### পুরনো video-র list দেখতে:
```bash
python main.py --logs
```

---

## কতটুকু ফ্রি, কতটুকু টাকা লাগবে?

| Service | ফ্রি কোটা | মাসে খরচ |
|---------|-----------|----------|
| Google Gemini | প্রতি মাসে 60 অনুরোধ/মিনিট ফ্রি | সাধারণত ফ্রিতেই চলবে |
| ElevenLabs | 10,000 chars/মাস ফ্রি | ফ্রিতেই চলবে (বেসিক ব্যবহারের জন্য) |
| Pollinations.ai (Image) | সম্পূর্ণ ফ্রি ✅ | ৳0 |
| YouTube API | সম্পূর্ণ ফ্রি ✅ | ৳0 |

---

## সমস্যা হলে
-   `video_log.json` দেখুন — কী হয়েছে record আছে
-   `output/script.json` দেখুন — script ঠিক হয়েছে কিনা
-   API key ভুল থাকলে error message আসবে
-   `modules/script_generator.py` এ `current_date` ফরম্যাটিং বাগটি ঠিক করে নিন: `"%2026"` এর পরিবর্তে `"%Y"` ব্যবহার করুন।
