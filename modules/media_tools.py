import os
import io
import base64
import requests
import qrcode
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes


# ---------- helpers ----------

def get_font(size):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    ]
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()


async def get_replied_photo_bytes(update: Update):
    msg = update.message.reply_to_message
    if not msg or not msg.photo:
        return None
    photo = msg.photo[-1]
    file = await photo.get_file()
    bio = io.BytesIO()
    await file.download_to_memory(bio)
    bio.seek(0)
    return bio


# ---------- /qr ----------

async def qr_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("Use: /qr <text>")
        return

    img = qrcode.make(text)
    bio = io.BytesIO()
    img.save(bio, format="PNG")
    bio.seek(0)
    await update.message.reply_photo(bio, caption="✅ QR code ready")


# ---------- /imgurl (imgBB) ----------

async def imgurl_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bio = await get_replied_photo_bytes(update)
    if bio is None:
        await update.message.reply_text("Kisi image ko reply karke /imgurl bhejo")
        return

    api_key = os.environ.get("IMGBB_API_KEY")
    if not api_key:
        await update.message.reply_text("⚠️ IMGBB_API_KEY environment variable set nahi hai")
        return

    b64 = base64.b64encode(bio.read()).decode()
    try:
        r = requests.post(
            "https://api.imgbb.com/1/upload",
            data={"key": api_key, "image": b64},
            timeout=30,
        )
        data = r.json()
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")
        return

    if data.get("success"):
        await update.message.reply_text(f"🔗 {data['data']['url']}")
    else:
        await update.message.reply_text("Upload fail ho gaya")


# ---------- /removebg ----------

async def removebg_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bio = await get_replied_photo_bytes(update)
    if bio is None:
        await update.message.reply_text("Image ko reply karke /removebg bhejo")
        return

    api_key = os.environ.get("REMOVEBG_API_KEY")
    if not api_key:
        await update.message.reply_text("⚠️ REMOVEBG_API_KEY environment variable set nahi hai")
        return

    try:
        response = requests.post(
            "https://api.remove.bg/v1.0/removebg",
            files={"image_file": bio},
            data={"size": "auto"},
            headers={"X-Api-Key": api_key},
            timeout=60,
        )
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")
        return

    if response.status_code == 200:
        out = io.BytesIO(response.content)
        out.seek(0)
        out.name = "nobg.png"
        await update.message.reply_document(out, caption="✅ Background removed")
    else:
        await update.message.reply_text(f"Error: {response.status_code} - {response.text[:200]}")


# ---------- /meme ----------

async def meme_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bio = await get_replied_photo_bytes(update)
    if bio is None:
        await update.message.reply_text("Image reply karo. Use: /meme top text | bottom text")
        return

    text = " ".join(context.args)
    parts = [p.strip() for p in text.split("|")]
    top = parts[0].upper() if len(parts) > 0 and parts[0] else ""
    bottom = parts[1].upper() if len(parts) > 1 and parts[1] else ""

    img = Image.open(bio).convert("RGB")
    draw = ImageDraw.Draw(img)
    w, h = img.size
    font_size = max(20, w // 10)
    font = get_font(font_size)

    def draw_centered(text, y):
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        x = (w - tw) / 2
        for ox, oy in [(-2, -2), (2, -2), (-2, 2), (2, 2), (0, 0)]:
            draw.text((x + ox, y + oy), text, font=font, fill="black")
        draw.text((x, y), text, font=font, fill="white")

    if top:
        draw_centered(top, 10)
    if bottom:
        draw_centered(bottom, h - font_size - 20)

    out = io.BytesIO()
    img.save(out, format="PNG")
    out.seek(0)
    await update.message.reply_photo(out, caption="✅ Meme ready")


# ---------- /resize ----------

async def resize_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bio = await get_replied_photo_bytes(update)
    if bio is None:
        await update.message.reply_text("Image reply karo. Use: /resize <width> <height>")
        return

    try:
        width, height = int(context.args[0]), int(context.args[1])
    except (IndexError, ValueError):
        await update.message.reply_text("Use: /resize <width> <height>")
        return

    img = Image.open(bio)
    img = img.resize((width, height))
    out = io.BytesIO()
    img.save(out, format="PNG")
    out.seek(0)
    out.name = "resized.png"
    await update.message.reply_document(out, caption=f"✅ Resized to {width}x{height}")


# ---------- /tts ----------

async def tts_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("Use: /tts <text>")
        return

    try:
        tts = gTTS(text=text, lang="hi")
        bio = io.BytesIO()
        tts.write_to_fp(bio)
        bio.seek(0)
        bio.name = "voice.mp3"
        await update.message.reply_voice(bio)
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


def register(app):
    app.add_handler(CommandHandler("qr", qr_cmd))
    app.add_handler(CommandHandler("imgurl", imgurl_cmd))
    app.add_handler(CommandHandler("removebg", removebg_cmd))
    app.add_handler(CommandHandler("meme", meme_cmd))
    app.add_handler(CommandHandler("resize", resize_cmd))
    app.add_handler(CommandHandler("tts", tts_cmd))
