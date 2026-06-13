import requests
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes


async def music_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("Use: /music <song name>")
        return

    try:
        r = requests.get(
            "https://api.deezer.com/search",
            params={"q": query},
            timeout=10,
        )
        results = r.json().get("data", [])[:5]
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")
        return

    if not results:
        await update.message.reply_text("Kuch nahi mila 🙁")
        return

    for track in results:
        title = track.get("title")
        artist = track.get("artist", {}).get("name")
        link = track.get("link")
        text = f"🎵 {title}\n👤 {artist}\n🔗 {link}"
        await update.message.reply_text(text)


def register(app):
    app.add_handler(CommandHandler("music", music_search))
