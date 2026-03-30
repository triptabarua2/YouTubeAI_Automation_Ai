# 🎬 YouTube AI Full Automation — সেটআপ গাইড (আপডেটেড)

## এই system কী করবে?
```
আপনি কিছু না করলেও প্রতিদিন ৩টি আলাদা চ্যানেলে:
Topic বাছাই → Script লেখা → AI Image বানানো → 
Multi-language Voiceover দেওয়া → Video Edit → YouTube Upload (অটোমেটিক শিডিউল)
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
3.  `config.py` তে `GOOGLE_API_KEY = "..."` এখানে বসান। (ভবিষ্যতে `.env` ফাইল ব্যবহার করার পরামর্শ দেওয়া হচ্ছে)

### B) ElevenLabs API Key (Voiceover — বাংলা, English, হিন্দি voice)
1.  https://elevenlabs.io যান
2.  Free Sign Up করুন এবং API Key কপি করুন।
3.  Voices → Voice Library থেকে আপনার পছন্দের ভয়েস বেছে নিন এবং তাদের Voice ID কপি করুন।
4.  `config.py` তে `ELEVENLABS_API_KEY`, `ELEVENLABS_VOICE_ID_BN`, `ELEVENLABS_VOICE_ID_EN`, `ELEVENLABS_VOICE_ID_HI` এখানে বসান।

### C) YouTube API (Upload করার জন্য)
1.  https://console.cloud.google.com যান এবং ৩টি চ্যানেলের জন্য আলাদা OAuth 2.0 Client ID তৈরি করুন।
2.  JSON ফাইলগুলো ডাউনলোড করে এই নামে সেভ করুন:
    - `client_secret_channel1.json`
    - `client_secret_channel2.json`
    - `client_secret_channel3.json`

---

## ধাপ ৪ — ৩টি চ্যানেলের সেটিংস (config.py)
আপনার ৩টি আলাদা চ্যানেলের জন্য `config.py` ফাইলে নিচের সেটিংসগুলো চেক করে নিন:
- **Channel 1:** Funny (সকাল ৯টা)
- **Channel 2:** Educational (দুপুর ১টা)
- **Channel 3:** Storytelling (রাত ৮টা)

---

## ধাপ ৫ — Run করুন!

### নির্দিষ্ট একটি চ্যানেল চালানো:
```bash
python main.py --channel channel_1 --auto-upload
```

### ৩টি চ্যানেল একসাথে চালানো (একটার পর একটা):
```bash
python main.py --all --auto-upload
```

### প্রতিদিন অটোমেটিক (Schedule Mode):
```bash
python main.py --schedule
```
> এটা চালিয়ে রাখলে `config.py` তে দেওয়া সময়ে প্রতিদিন ৩টি চ্যানেলে ভিডিও আপলোড হবে!

---

## নিরাপত্তা ও সতর্কতা (Security Warning)
- আপনার `config.py` ফাইলে সরাসরি API Key দেওয়া আছে। এগুলো কখনোই পাবলিকলি শেয়ার করবেন না।
- `.gitignore` ফাইলে আপনার সিক্রেট ফাইলগুলো (`client_secret*.json`, `token*.pickle`) অলরেডি অ্যাড করা আছে, তাই এগুলো গিথাবে আপলোড হবে না।

---

## সমস্যা হলে
- `video_log.json` দেখুন — ভিডিও তৈরির হিস্ট্রি এবং এরর এখানে পাবেন।
- `output/` ফোল্ডারে প্রতিটি চ্যানেলের আলাদা আউটপুট ভিডিও এবং স্ক্রিপ্ট সেভ হবে।
- যদি ভিডিও এডিটরে কোনো সমস্যা হয়, তবে `modules/video_editor.py`-তে ফন্ট সেটিংস চেক করুন।
