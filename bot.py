import os
import logging
from time import monotonic
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "PASTE_TOKEN_HERE")
COOLDOWN_SECONDS = int(os.getenv("COOLDOWN_SECONDS", "30"))

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("admin-caller")

_cooldowns = {}

async def _build_admin_mentions(chat_id: int, bot) -> list[str]:
    admins = await bot.get_chat_administrators(chat_id)
    mentions = []
    for admin in admins:
        user = admin.user
        if user.is_bot:
            continue
        if user.username:
            mentions.append(f"@{user.username}")
        else:
            mentions.append(user.mention_html())
    return mentions

def _can_alert_now(chat_id: int) -> bool:
    now = monotonic()
    last = _cooldowns.get(chat_id, 0.0)
    if now - last < COOLDOWN_SECONDS:
        return False
    _cooldowns[chat_id] = now
    return True

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот для вызова модерации.\n"
        "/call — позвать всех админов\n"
        "/setup — выслать кнопку с вызовом модерации"
    )

async def call_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if not _can_alert_now(chat.id):
        await update.message.reply_text("⏳ Уже был вызов недавно, подожди немного.")
        return
    mentions = await _build_admin_mentions(chat.id, context.bot)
    if not mentions:
        await update.message.reply_text("Админов не найдено 🤷")
        return
    await update.message.reply_html("🚨 Вызов модерации: " + " ".join(mentions))

async def setup_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🚨 Позвать модераторов", callback_data="panic")]]
    )
    await update.message.reply_text("Кнопка для вызова модерации:", reply_markup=keyboard)

async def panic_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat = query.message.chat
    if not _can_alert_now(chat.id):
        await query.message.reply_text("⏳ Уже был вызов недавно, подожди немного.")
        return
    mentions = await _build_admin_mentions(chat.id, context.bot)
    if not mentions:
        await query.message.reply_text("Админов не найдено 🤷")
        return
    await query.message.reply_html("🚨 Срочно нужна помощь: " + " ".join(mentions))

def main():
    if not TOKEN or TOKEN == "PASTE_TOKEN_HERE":
        raise SystemExit("Укажи токен в TELEGRAM_BOT_TOKEN")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("call", call_cmd))
    app.add_handler(CommandHandler("setup", setup_cmd))
    app.add_handler(CallbackQueryHandler(panic_cb, pattern="^panic$"))
    logger.info("Бот запущен 🚀")
    app.run_polling()

if __name__ == "__main__":
    main()
