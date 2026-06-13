import sqlite3
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, ContextTypes, filters

DB_PATH = "stats.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS stats (
            chat_id INTEGER,
            user_id INTEGER,
            name TEXT,
            count INTEGER,
            PRIMARY KEY (chat_id, user_id)
        )"""
    )
    conn.commit()
    conn.close()


async def track_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or update.effective_chat.type == "private":
        return
    if not update.effective_user:
        return

    chat_id = update.effective_chat.id
    user = update.effective_user
    name = user.first_name or user.username or "Unknown"

    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """INSERT INTO stats (chat_id, user_id, name, count) VALUES (?, ?, ?, 1)
           ON CONFLICT(chat_id, user_id) DO UPDATE SET count = count + 1, name = ?""",
        (chat_id, user.id, name, name),
    )
    conn.commit()
    conn.close()


async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT name, count FROM stats WHERE chat_id = ? ORDER BY count DESC LIMIT 10",
        (chat_id,),
    ).fetchall()
    conn.close()

    if not rows:
        await update.message.reply_text("Abhi tak koi activity data nahi hai")
        return

    text = "📊 *Top Active Members*\n\n"
    medals = ["🥇", "🥈", "🥉"]
    for i, (name, count) in enumerate(rows):
        prefix = medals[i] if i < 3 else f"{i + 1}."
        text += f"{prefix} {name} — {count} messages\n"

    await update.message.reply_text(text, parse_mode="Markdown")


def register(app):
    init_db()
    # group=1 so it runs alongside command handlers (default group 0)
    app.add_handler(
        MessageHandler(filters.ALL & filters.ChatType.GROUPS, track_message),
        group=1,
    )
    app.add_handler(CommandHandler("stats", stats_cmd))
