# modules/image_generator.py
# Pollinations.ai দিয়ে FREE AI image তৈরি করে (কোনো API key লাগে না!)

import requests, os, time
from PIL import Image
from io import BytesIO

DEFAULT_OUTPUT_DIR = "temp/images"


def generate_image(prompt: str, filename: str,
                   width: int = 1920, height: int = 1080,
                   output_dir: str = None) -> str:
    out = output_dir or DEFAULT_OUTPUT_DIR
    os.makedirs(out, exist_ok=True)
    filepath = os.path.join(out, filename)

    full_prompt = f"{prompt}, 2D flat animation style, vibrant colors, clean lines, cartoon, professional illustration, no text"
    full_prompt = full_prompt.replace(" ", "%20")
    url = f"https://image.pollinations.ai/prompt/{full_prompt}?width={width}&height={height}&nologo=true"

    print(f"  🎨 Image: {filename}")
    for attempt in range(3):
        try:
            response = requests.get(url, timeout=60)
            if response.status_code == 200:
                img = Image.open(BytesIO(response.content))
                img.save(filepath, "PNG")
                print(f"  ✅ Saved: {filepath}")
                time.sleep(2)
                return filepath
        except Exception as e:
            print(f"  ⚠️ Attempt {attempt+1} failed: {e}")
            time.sleep(5)

    # Fallback
    img = Image.new("RGB", (width, height), color=(26, 26, 46))
    img.save(filepath, "PNG")
    return filepath


def generate_thumbnail(prompt: str, title: str,
                       temp_dir: str = None) -> str:
    out = os.path.join(temp_dir, "images") if temp_dir else DEFAULT_OUTPUT_DIR
    thumb_prompt = f"{prompt}, YouTube thumbnail, bold composition, eye-catching, 2D animation style"
    return generate_image(thumb_prompt, "thumbnail.png", 1280, 720, output_dir=out)


def generate_all_scene_images(scenes: list, temp_dir: str = None) -> list:
    out = os.path.join(temp_dir, "images") if temp_dir else DEFAULT_OUTPUT_DIR
    print(f"\n🎨 {len(scenes)}টি scene image তৈরি হচ্ছে...")
    paths = []
    for scene in scenes:
        n    = scene["scene_number"]
        path = generate_image(scene["image_prompt"], f"scene_{n:02d}.png", output_dir=out)
        paths.append(path)
    print("✅ সব image তৈরি!")
    return paths
