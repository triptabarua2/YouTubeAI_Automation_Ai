# modules/script_generator.py
# Groq API দিয়ে channel-এর topic অনুযায়ী script তৈরি করে
# ✅ Updated: Gemini → Groq (ফ্রি + fast)

from groq import Groq
import json, sys, os, datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GROQ_API_KEY, SCENES_PER_VIDEO

# Model name
MODEL = "llama-3.3-70b-versatile"


def generate_script(topic: str, channel_style: str = "", topic_type: str = "funny") -> dict:
    print(f"📝 Script তৈরি হচ্ছে: '{topic}' [{topic_type}]")

    client = Groq(api_key=GROQ_API_KEY)

    style_instructions = {
        "funny": "Use Bengali slang, jokes, puns, exaggerated humor. Tone: like a funny friend telling a story.",
        "educational": "Use clear facts, interesting trivia, easy explanations. Tone: friendly teacher.",
        "storytelling": "Use suspense, dramatic pauses, mystery. Tone: thrilling narrator.",
    }
    style_note = style_instructions.get(topic_type, style_instructions["funny"])

    prompt = f"""You are a Bengali YouTube animator creating a {topic_type} animated video.

Topic: "{topic}"
Channel Style: {channel_style}
Style Note: {style_note}

For each scene provide narration in THREE languages: Bengali, Hindi, English.

Return ONLY valid JSON, no explanation, no markdown:
{{
  "title": "Clickbait Bengali title with emoji",
  "description": "Bengali description (150 words) with emoji",
  "tags": ["tag1", "tag2", "animation", "bengali", "বাংলা"],
  "mood": "{topic_type}",
  "scenes": [
    {{
      "scene_number": 1,
      "duration_seconds": 20,
      "narration": "Bengali narration",
      "translation_hindi": "Hindi translation",
      "translation_english": "English translation",
      "joke": "Funny/interesting one-liner in Bengali",
      "character_emotion": "shocked / laughing / facepalm / jumping / confused / proud / scared / crying_laugh",
      "visual_description": "Scene description in English",
      "image_prompt": "2D animation scene, cartoon style, bright colors"
    }}
  ],
  "thumbnail_prompt": "Eye-catching thumbnail, 2D animation style",
  "hook": "First line that grabs attention in 3 seconds"
}}

Make exactly {SCENES_PER_VIDEO} scenes.
"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=4000,
        )
        text = response.choices[0].message.content.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        data = json.loads(text)
        print(f"✅ Script তৈরি: {len(data['scenes'])} scenes [{topic_type}]")
        return data
    except Exception as e:
        print(f"❌ Script generation error: {e}")
        return {"title": topic, "scenes": []}


def get_trending_topic(topic_type: str = "funny", topic_description: str = "") -> str:
    client = Groq(api_key=GROQ_API_KEY)

    date = datetime.date.today().strftime("%B %d, %Y")

    prompt = f"""Today is {date}.
Find ONE viral/trending topic in Bangladesh for a {topic_type} Bengali animation channel.
Channel focus: {topic_description}

Return ONLY the topic in Bengali with a relevant emoji. No explanation, no extra text.
Example: "বিদ্যুৎ বিল দেখে মধ্যবিত্তের হার্ট অ্যাটাক 😂"
"""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,
            max_tokens=100,
        )
        topic = response.choices[0].message.content.strip()
        print(f"💡 Trending Topic [{topic_type}]: {topic}")
        return topic
    except Exception as e:
        print(f"⚠️ Topic fetch error: {e}")
        return f"বাংলাদেশের আজকের সেরা মুহূর্ত 🔥"
