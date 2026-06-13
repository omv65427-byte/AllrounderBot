# Multi-Feature Telegram Bot

20 features in one bot: music search, captcha verification, group stats,
file compress/decompress, QR codes, image-to-URL, backup, meme generator,
background remover, image resize, PDF tools, currency converter, URL
shortener, text-to-speech, OCR, reminders, polls, dictionary, and translation.

## 📁 Project Structure

```
telegram-bot/
├── main.py              # Entry point, registers all modules
├── modules/
│   ├── music.py         # /music
│   ├── media_tools.py    # /qr /imgurl /removebg /meme /resize /tts
│   ├── file_tools.py     # /compress /decompress /pdf2img /img2pdf
│   ├── utility.py        # /currency /shorten /dictionary /translate /ocr
│   ├── reminders.py       # /remind /poll
│   ├── captcha.py          # New member verification
│   └── group_stats.py      # /stats - activity tracking
├── requirements.txt
├── Procfile
├── runtime.txt
└── .env.example
```

## 🚀 Setup (Local Test)

1. Get a bot token from [@BotFather](https://t.me/BotFather) on Telegram.
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in `BOT_TOKEN` (others optional).
4. Run:
   ```
   python main.py
   ```

## 🚂 Deploy on Railway

1. Push this folder to a GitHub repo.
2. On [Railway](https://railway.app), create a **New Project → Deploy from GitHub repo**.
3. Railway auto-detects `requirements.txt` and `Procfile`.
4. Go to **Variables** tab and add the environment variables below.
5. Deploy. Bot runs as a `worker` (polling mode, no public URL needed).

## 🔑 Environment Variables (Railway → Variables)

| Variable | Required? | Where to get it |
|---|---|---|
| `BOT_TOKEN` | ✅ Yes | [@BotFather](https://t.me/BotFather) |
| `IMGBB_API_KEY` | Optional (for `/imgurl`) | [api.imgbb.com](https://api.imgbb.com/) |
| `REMOVEBG_API_KEY` | Optional (for `/removebg`) | [remove.bg/api](https://www.remove.bg/api) |
| `OCR_API_KEY` | Optional (for `/ocr`) | [ocr.space/ocrapi](https://ocr.space/ocrapi) |

If optional keys are missing, those specific commands reply with a warning —
everything else works fine.

## 🛠️ All Commands

**Music**
- `/music <name>` — Song search via Deezer

**Image Tools** (reply to an image)
- `/qr <text>` — Generate QR code
- `/imgurl` — Upload image, get direct URL
- `/removebg` — Remove background
- `/meme <top> | <bottom>` — Make a meme
- `/resize <w> <h>` — Resize image
- `/ocr` — Extract text from image

**File Tools**
- `/compress` (reply to file) — Zip a file
- `/decompress` (reply to .zip/.7z) — Extract files
- `/pdf2img` (reply to PDF) — Convert pages to images
- `/img2pdf` (reply to image) — Convert image to PDF

**Utility**
- `/currency <amt> <from> <to>` — Currency conversion
- `/shorten <url>` — Shorten a URL
- `/dictionary <word>` — Word meaning
- `/translate <lang_code> <text>` — Translate text
- `/tts <text>` — Text to voice note

**Productivity**
- `/remind <minutes> <message>` — Set a reminder
- `/poll <question> | <opt1> | <opt2> ...` — Create a poll

**Group**
- New members get a math captcha before they can chat
- `/stats` — Top active members in the group

## 📝 Notes

- `group_stats.py` uses a local SQLite file (`stats.db`). On Railway's
  default ephemeral filesystem, this resets on redeploy — fine for casual
  use, but add a [Railway Volume](https://docs.railway.app/reference/volumes)
  if you want it persistent.
- Captcha state is in-memory and resets on restart.
- The bot requires **admin rights** in groups to restrict/verify new members.
