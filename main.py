import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from modules import music, media_tools, file_tools, utility, reminders, captcha, group_stats

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")

HELP_TEXT = """🤖 *Available Commands*

🎵 *Music*
/music <name> - Song search (Deezer)

🖼️ *Image Tools* (reply to an image)
/qr <text> - Generate QR code
/imgurl - Upload image, get direct URL
/removebg - Remove background
/meme <top> | <bottom> - Make a meme
/resize <w> <h> - Resize image
/ocr - Extract text from image

📁 *File Tools*
/compress - Compress a file (reply to file)
/decompress - Extract zip/7z (reply to file)
/pdf2img - PDF pages to images (reply to pdf)
/img2pdf - Image to PDF (reply to image)

🔧 *Utility*
/currency <amt> <from> <to> - Convert currency
/shorten <url> - Shorten a URL
/dictionary <word> - Word meaning
/translate <lang-code> <text> - Translate text
/tts <text> - Text to voice message

⏰ *Productivity*
/remind <minutes> <message> - Set a reminder
/poll <question> | <opt1> | <opt2> ... - Create a poll

👥 *Group*
/stats - Top active members
(New members get a captcha to verify)
"""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome! Main multi-feature bot hu.\n/help likho saare commands dekhne ke liye."
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_TEXT, parse_mode="Markdown")


def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN environment variable not set")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))

    # Register feature modules
    music.register(app)
    media_tools.register(app)
    file_tools.register(app)
    utility.register(app)
    reminders.register(app)
    captcha.register(app)
    group_stats.register(app)

    logger.info("Bot starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
