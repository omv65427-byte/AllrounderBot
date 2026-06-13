import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.ext import MessageHandler, CallbackQueryHandler, ContextTypes, filters

# In-memory store of pending verifications: {(chat_id, user_id): correct_answer}
pending = {}


async def new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    for member in update.message.new_chat_members:
        if member.is_bot:
            continue

        a, b = random.randint(1, 9), random.randint(1, 9)
        answer = a + b
        pending[(chat_id, member.id)] = answer

        try:
            await context.bot.restrict_chat_member(
                chat_id,
                member.id,
                permissions=ChatPermissions(can_send_messages=False),
            )
        except Exception:
            pass  # bot may not have admin rights

        options = list({answer, answer + 1, answer - 1, answer + 2})
        while len(options) < 4:
            options.append(answer + len(options) + 3)
        random.shuffle(options)

        buttons = [
            InlineKeyboardButton(str(o), callback_data=f"captcha_{member.id}_{o}")
            for o in options
        ]

        await update.message.reply_text(
            f"👋 Welcome {member.first_name}!\nSpam-bot na ho, isliye solve karo: {a} + {b} = ?",
            reply_markup=InlineKeyboardMarkup([buttons]),
        )


async def captcha_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    _, uid_str, ans_str = query.data.split("_")
    uid, ans = int(uid_str), int(ans_str)
    chat_id = query.message.chat_id

    if query.from_user.id != uid:
        await query.answer("Yeh verification tumhare liye nahi hai", show_alert=True)
        return

    correct = pending.get((chat_id, uid))

    if correct is None:
        await query.answer("Already verified ya expired")
        return

    if ans == correct:
        try:
            await context.bot.restrict_chat_member(
                chat_id,
                uid,
                permissions=ChatPermissions(
                    can_send_messages=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True,
                    can_send_polls=True,
                ),
            )
        except Exception:
            pass

        await query.edit_message_text(f"✅ {query.from_user.first_name} verified!")
        pending.pop((chat_id, uid), None)
    else:
        await query.answer("❌ Galat jawab, dobara try karo", show_alert=True)


def register(app):
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_member))
    app.add_handler(CallbackQueryHandler(captcha_button, pattern=r"^captcha_"))
