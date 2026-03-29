# modules/video_editor.py
# Character-driven video — 2D character মূল presenter হিসেবে থাকবে
# Features:
#   - সাদা background auto-remove (transparent character)
#   - Breathing + talking animation
#   - Slide-in entrance effect
#   - Scene background (AI generated) পেছনে, character সামনে
#   - নিচে subtitle bar

import os
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from moviepy import (
    VideoClip, ImageClip, AudioFileClip, CompositeAudioClip,
    concatenate_videoclips, CompositeVideoClip, ColorClip
)

OUTPUT_DIR = "output"
ASSETS_DIR = "assets"
CHAR_CACHE  = os.path.join(ASSETS_DIR, "character_transparent.png")  # processed একবার


# ──────────────────────────────────────────────────────────────
#  1. সাদা background remove করা (একবারই করা হবে)
# ──────────────────────────────────────────────────────────────

def remove_white_background(src_path: str, dst_path: str, threshold: int = 230) -> str:
    """
    character.png-এর সাদা background সরিয়ে transparent PNG বানায়।
    threshold: 0-255 — বেশি হলে বেশি সাদা remove হবে
    """
    img = Image.open(src_path).convert("RGBA")
    data = np.array(img, dtype=np.float32)

    r, g, b, a = data[:,:,0], data[:,:,1], data[:,:,2], data[:,:,3]

    # সাদার কাছাকাছি pixel গুলো transparent করা
    white_mask = (r > threshold) & (g > threshold) & (b > threshold)

    # Edge softening — হার্ড কাটা না হয়ে smooth হবে
    from PIL import ImageFilter
    mask_img = Image.fromarray(white_mask.astype(np.uint8) * 255, "L")
    mask_img = mask_img.filter(ImageFilter.GaussianBlur(radius=1))
    soft_mask = np.array(mask_img) / 255.0

    data[:,:,3] = a * (1.0 - soft_mask)
    result = Image.fromarray(data.astype(np.uint8), "RGBA")
    result.save(dst_path, "PNG")
    print(f"  ✅ Character background removed → {dst_path}")
    return dst_path


def get_character_image() -> Image.Image:
    """Character PNG load করে (processed transparent version)"""
    char_src = os.path.join(ASSETS_DIR, "character.png")

    if not os.path.exists(char_src):
        print("  ⚠️ character.png পাওয়া যায়নি")
        return None

    # একবার process করলে cache use করে
    if not os.path.exists(CHAR_CACHE):
        os.makedirs(ASSETS_DIR, exist_ok=True)
        remove_white_background(char_src, CHAR_CACHE)

    return Image.open(CHAR_CACHE).convert("RGBA")


# ──────────────────────────────────────────────────────────────
#  2. Ken Burns effect — background-এর জন্য
# ──────────────────────────────────────────────────────────────

def make_background_clip(image_path: str, duration: float, effect: str = "in") -> VideoClip:
    """AI-generated scene image-এ Ken Burns effect"""
    img = Image.open(image_path).convert("RGB")
    W, H = img.size
    arr = np.array(img)

    def make_frame(t):
        p = t / duration
        if effect == "in":
            scale = 1.0 + 0.12 * p
        elif effect == "out":
            scale = 1.12 - 0.12 * p
        elif effect == "pan_right":
            scale = 1.1
        elif effect == "pan_left":
            scale = 1.1
        else:
            scale = 1.05

        nw, nh = int(W * scale), int(H * scale)
        resized = Image.fromarray(arr).resize((nw, nh), Image.Resampling.LANCZOS)

        left = (nw - W) // 2
        top  = (nh - H) // 2

        if effect == "pan_right":
            left = int(p * (nw - W))
        elif effect == "pan_left":
            left = int((1 - p) * (nw - W))

        cropped = resized.crop((left, top, left + W, top + H))
        return np.array(cropped)

    return VideoClip(make_frame, duration=duration).with_fps(24)


# ──────────────────────────────────────────────────────────────
#  3. Character animation frame builder
# ──────────────────────────────────────────────────────────────

def make_character_frames(char_img: Image.Image, video_w: int, video_h: int,
                           duration: float, side: str = "right",
                           entrance: bool = True) -> VideoClip:
    """
    Character-এর animated clip বানায়।
    Animations:
      - Breathing: ওপর-নিচে ধীরে ওঠানামা
      - Talking: হালকা scale pulse (বলার সময় একটু নড়াচড়া)
      - Entrance: নিচ থেকে slide-in (প্রথম ০.৪ সেকেন্ড)
      - Head bob: খুব সূক্ষ্ম বাঁয়ে-ডানে দোলা
    """
    # Character size: video height-এর ৬৫%
    target_h = int(video_h * 0.65)
    ratio    = target_h / char_img.height
    target_w = int(char_img.width * ratio)
    char_resized = char_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    char_arr = np.array(char_resized)  # RGBA

    # Position
    margin = 40
    if side == "right":
        base_x = video_w - target_w - margin
    else:
        base_x = margin
    base_y = video_h - target_h  # পায়ের কাছে নিচে

    entrance_frames = int(0.4 * 24)  # ০.৪ সেকেন্ড entrance

    def make_frame(t):
        # ── Animations ──
        # 1. Breathing: 0.4 Hz sine
        breathe_y = int(6 * np.sin(2 * np.pi * 0.4 * t))

        # 2. Talking pulse: ছোট scale variation
        talk_scale = 1.0 + 0.012 * np.sin(2 * np.pi * 3.5 * t)

        # 3. Head bob: ০.২ Hz, ±৩px horizontal
        head_x = int(3 * np.sin(2 * np.pi * 0.2 * t))

        # 4. Entrance slide-in
        frame_idx = int(t * 24)
        if entrance and frame_idx < entrance_frames:
            progress   = frame_idx / entrance_frames
            ease       = 1 - (1 - progress) ** 3  # ease-out cubic
            slide_y    = int((1 - ease) * target_h)
        else:
            slide_y = 0

        cur_y = base_y + breathe_y + slide_y
        cur_x = base_x + head_x

        # ── Canvas ── (transparent RGBA)
        canvas = Image.new("RGBA", (video_w, video_h), (0, 0, 0, 0))

        # Talking scale apply
        if abs(talk_scale - 1.0) > 0.001:
            new_w = int(target_w * talk_scale)
            new_h = int(target_h * talk_scale)
            char_frame = Image.fromarray(char_arr).resize(
                (new_w, new_h), Image.Resampling.LANCZOS)
            # Center adjust
            cur_x -= (new_w - target_w) // 2
            cur_y -= (new_h - target_h)
        else:
            char_frame = Image.fromarray(char_arr)

        # Character paste
        canvas.paste(char_frame, (cur_x, cur_y), char_frame)

        return np.array(canvas)

    def make_mask(t):
        frame = make_frame(t)
        return frame[:, :, 3] / 255.0

    rgb_clip  = VideoClip(lambda t: make_frame(t)[:, :, :3], duration=duration)
    mask_clip = VideoClip(make_mask, duration=duration, is_mask=True)
    return rgb_clip.with_mask(mask_clip).with_fps(24)


# ──────────────────────────────────────────────────────────────
#  4. Subtitle bar
# ──────────────────────────────────────────────────────────────

def make_subtitle_clip(text: str, video_w: int, video_h: int, duration: float) -> VideoClip:
    """নিচে semi-transparent subtitle bar"""
    bar_h = 110

    def make_frame(t):
        canvas = Image.new("RGBA", (video_w, video_h), (0, 0, 0, 0))
        draw   = ImageDraw.Draw(canvas)

        # Gradient bar
        for y in range(bar_h):
            alpha = int(180 * (1 - y / bar_h * 0.3))
            draw.line([(0, video_h - bar_h + y), (video_w, video_h - bar_h + y)],
                      fill=(10, 10, 30, alpha))

        # Text
        display = text[:72] + "..." if len(text) > 72 else text
        try:
            font = ImageFont.load_default(size=34)
        except TypeError:
            font = ImageFont.load_default()

        # Shadow
        draw.text((video_w // 2 + 2, video_h - bar_h // 2 + 2),
                  display, fill=(0, 0, 0, 200), anchor="mm", font=font)
        # Main text
        draw.text((video_w // 2, video_h - bar_h // 2),
                  display, fill=(255, 255, 255, 255), anchor="mm", font=font)

        return np.array(canvas)

    def make_mask(t):
        return make_frame(t)[:, :, 3] / 255.0

    rgb  = VideoClip(lambda t: make_frame(t)[:, :, :3], duration=duration)
    mask = VideoClip(make_mask, duration=duration, is_mask=True)
    return rgb.with_mask(mask).with_fps(24)


# ──────────────────────────────────────────────────────────────
#  5. Main video creator
# ──────────────────────────────────────────────────────────────

def create_video(scenes: list, image_paths: list, audio_paths: list,
                 output_filename: str, music_path: str = None) -> str:
    """
    প্রতিটি scene-এ:
      Background (AI image, Ken Burns)  ← পেছনে
      + Character (animated presenter)  ← সামনে
      + Subtitle bar                    ← নিচে
      + Voiceover audio
    """
    print("\n🎬 Video তৈরি হচ্ছে (Character-driven mode)...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Character একবার load
    char_img = get_character_image()
    if char_img is None:
        print("  ⚠️ Character ছাড়াই চলবে")

    VIDEO_W, VIDEO_H = 1920, 1080
    effects = ["in", "out", "pan_right", "pan_left"]
    sides   = ["right", "left"]
    clips   = []

    for i, (scene, img_path, audio_path) in enumerate(
            zip(scenes, image_paths, audio_paths)):
        print(f"  🎞️  Scene {i+1}/{len(scenes)} তৈরি হচ্ছে...")

        try:
            audio_clip = AudioFileClip(audio_path)
            duration   = audio_clip.duration

            # ── Layer 1: Background ──
            bg = make_background_clip(img_path, duration, effects[i % len(effects)])

            layers = [bg]

            # ── Layer 2: Character ──
            if char_img is not None:
                side     = sides[i % len(sides)]
                entrance = (i == 0)  # শুধু প্রথম scene-এ slide-in
                char_clip = make_character_frames(
                    char_img, VIDEO_W, VIDEO_H, duration, side, entrance)
                layers.append(char_clip)

            # ── Layer 3: Subtitle ──
            sub = make_subtitle_clip(scene["narration"], VIDEO_W, VIDEO_H, duration)
            layers.append(sub)

            # ── Composite ──
            composite = CompositeVideoClip(layers, size=(VIDEO_W, VIDEO_H))
            composite = composite.with_audio(audio_clip).with_fps(24)

            clips.append(composite)

        except Exception as e:
            print(f"  ⚠️ Scene {i+1} error: {e}")
            import traceback; traceback.print_exc()

    if not clips:
        raise ValueError("কোনো clip তৈরি হয়নি!")

    print("  🔗 Clips জোড়া লাগানো হচ্ছে...")
    final = concatenate_videoclips(clips, method="compose")

    # ── Background Music ──
    if music_path and os.path.exists(music_path):
        print(f"  🎵 Background music মেশানো হচ্ছে...")
        try:
            bg_music = AudioFileClip(music_path).with_volume_scaled(0.1)
            if bg_music.duration < final.duration:
                # Loop করা
                repeats = int(final.duration / bg_music.duration) + 1
                from moviepy import concatenate_audioclips
                bg_music = concatenate_audioclips([bg_music] * repeats)
            bg_music = bg_music.with_section(0, final.duration)
            mixed = CompositeAudioClip([final.audio, bg_music])
            final = final.with_audio(mixed)
        except Exception as e:
            print(f"  ⚠️ Music error: {e}")

    output_path = os.path.join(OUTPUT_DIR, output_filename)
    print("  💾 Video export হচ্ছে (কিছুটা সময় লাগবে)...")
    final.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        logger=None
    )

    print(f"  ✅ Video তৈরি হয়েছে: {output_path}")
    return output_path
