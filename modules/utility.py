import os
import io
import requests
from deep_translator import GoogleTranslator
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes


# ---------- /currency ----------

async def currency_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amount = float(context.args[0])
        frm = context.args[1].upper()
        to = context.args[2].upper()
    except (IndexError, ValueError):
        await update.message.reply_text("Use: /currency <amount> <from> <to>\nExample: /currency 100 USD INR")
        return

    try:
        r = requests.get(
            "https://api.frankfurter.app/latest",
            params={"amount": amount, "from": frm, "to": to},
            timeout=10,
        )
        data = r.json()
        rate = data.get("rates", {}).get(to)
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")
        return

    if rate is not None:
        await update.message.reply_text(f"💱 {amount} {frm} = {rate} {to}")
    else:
        await update.message.reply_text("Conversion fail, currency code check karo")


# ---------- /shorten ----------

async def shorten_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = " ".join(context.args)
    if not url:
        await update.message.reply_text("Use: /shorten <url>")
        return

    try:
        r = requests.get(
            "https://tinyurl.com/api-create.php",
            params={"url": url},
            timeout=10,
        )
        if r.status_code == 200 and r.text.startswith("http"):
            await update.message.reply_text(f"🔗 {r.text}")
        else:
            await update.message.reply_text("Shorten fail ho gaya")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


# ---------- /dictionary ----------

async def dictionary_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    word = " ".join(context.args)
    if not word:
        await update.message.reply_text("Use: /dictionary <word>")
        return

    try:
        r = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}", timeout=10)
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")
        return

    if r.status_code != 200:
        await update.message.reply_text("Word nahi mila")
        return

    data = r.json()[0]
    meanings = data.get("meanings", [])
    text = f"📖 {word}\n"
    for m in meanings[:3]:
        pos = m.get("partOfSpeech", "")
        defs = m.get("definitions", [])
        if defs:
            text += f"\n({pos}): {defs[0].get('definition')}"
    await update.message.reply_text(text)


# ---------- /translate ----------

async def translate_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Use: /translate <lang_code> <text>\nExample: /translate hi Hello world")
        return

    lang = context.args[0]
    text = " ".join(context.args[1:])

    try:
        result = GoogleTranslator(source="auto", target=lang).translate(text)
        await update.message.reply_text(result)
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


# ---------- /ocr ----------

async def ocr_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.reply_to_message
    if not msg or not msg.photo:
        await update.message.reply_text("Image ko reply karke /ocr bhejo")
        return

    api_key = os.environ.get("OCR_API_KEY", "helloworld")  # 'helloworld' = free demo key, limited usage

    photo = msg.photo[-1]
    file = await photo.get_file()
    bio = io.BytesIO()
    await file.download_to_memory(bio)
    bio.seek(0)

    try:
        r = requests.post(
            "https://api.ocr.space/parse/image",
            files={"file": ("image.jpg", bio)},
            data={"apikey": api_key},
            timeout=30,
        )
        data = r.json()
        text = data["ParsedResults"][0]["ParsedText"].strip()
        await update.message.reply_text(text or "Koi text nahi mila")
    except Exception as e:
        await update.message.reply_text(f"OCR fail: {e}")


def register(app):
    app.add_handler(CommandHandler("currency", currency_cmd))
    app.add_handler(CommandHandler("shorten", shorten_cmd))
    app.add_handler(CommandHandler("dictionary", dictionary_cmd))
    app.add_handler(CommandHandler("translate", translate_cmd))
    app.add_handler(CommandHandler("ocr", ocr_cmd))
