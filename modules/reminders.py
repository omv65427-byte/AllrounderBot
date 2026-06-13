from telegram import Update
from telegram.ext import CommandHandler, ContextTypes


# ---------- /remind ----------

async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    data = context.job.data
    await context.bot.send_message(
        chat_id=data["chat_id"],
        text=f"⏰ {data['user']}, reminder: {data['msg']}",
    )


async def remind_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Use: /remind <minutes> <message>")
        return

    try:
        minutes = float(context.args[0])
    except ValueError:
        await update.message.reply_text("Minutes ek number hona chahiye")
        return

    message = " ".join(context.args[1:])
    chat_id = update.effective_chat.id
    user = update.effective_user.first_name

    context.job_queue.run_once(
        send_reminder,
        when=minutes * 60,
        data={"chat_id": chat_id, "msg": message, "user": user},
    )
    await update.message.reply_text(f"✅ Reminder set for {minutes} min baad")


# ---------- /poll ----------

async def poll_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    parts = [p.strip() for p in text.split("|") if p.strip()]

    if len(parts) < 3:
        await update.message.reply_text(
            "Use: /poll question | option1 | option2 | ...\n(Min 2 options)"
        )
        return

    question = parts[0]
    options = parts[1:10]  # Telegram allows max 10 options

    await update.effective_chat.send_poll(
        question=question,
        options=options,
        is_anonymous=False,
    )


def register(app):
    app.add_handler(CommandHandler("remind", remind_cmd))
    app.add_handler(CommandHandler("poll", poll_cmd))
