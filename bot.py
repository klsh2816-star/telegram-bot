import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 1503910952

app_web = Flask(__name__)


@app_web.route("/")
def home():
    return "Telegram Bot is running!"


def run_bot():
    application = Application.builder().token(TOKEN).build()

    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [InlineKeyboardButton("🏠 صفحه اصلی", callback_data="home")],
            [InlineKeyboardButton("👤 پروفایل", callback_data="profile")],
            [InlineKeyboardButton("📚 آموزش‌ها", callback_data="courses")],
            [InlineKeyboardButton("ℹ️ درباره ما", callback_data="about")],
            [InlineKeyboardButton("📝 گزارش", callback_data="report")]
        ]

        await update.message.reply_text(
            "سلام 👋\nبه ربات خوش آمدی.\n\nیک گزینه را انتخاب کن:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        if query.data == "home":
            await query.edit_message_text(
                "🏠 صفحه اصلی\n\nبه صفحه اصلی ربات خوش آمدی."
            )

        elif query.data == "profile":
            user = query.from_user

            await query.edit_message_text(
                f"👤 پروفایل\n\n"
                f"نام: {user.first_name}\n"
                f"Username: @{user.username if user.username else 'ندارد'}\n"
                f"ID: {user.id}"
            )

        elif query.data == "courses":
            await query.edit_message_text(
                "📚 آموزش‌ها\n\n"
                "آموزش‌های ربات به‌زودی در این بخش قرار می‌گیرند."
            )

        elif query.data == "about":
            await query.edit_message_text(
                "ℹ️ درباره ما\n\n"
                "به ربات ما خوش آمدید."
            )

        elif query.data == "report":
            context.user_data["reporting"] = True

            await query.edit_message_text(
                "📝 گزارش\n\n"
                "لطفاً گزارش خود را در یک پیام بنویسید."
            )

    async def receive_report(update: Update, context: ContextTypes.DEFAULT_TYPE):

        if not context.user_data.get("reporting"):
            return

        user = update.effective_user
        report = update.message.text

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                "🚨 گزارش جدید\n\n"
                f"👤 نام: {user.first_name}\n"
                f"🆔 ID: {user.id}\n"
                f"📱 Username: @{user.username if user.username else 'ندارد'}\n\n"
                f"📝 متن گزارش:\n{report}"
            )
        )

        context.user_data["reporting"] = False

        await update.message.reply_text(
            "✅ گزارش شما با موفقیت برای مدیریت ارسال شد."
        )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(buttons))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, receive_report)
    )

    application.run_polling(stop_signals=None)


threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app_web.run(host="0.0.0.0", port=port)
