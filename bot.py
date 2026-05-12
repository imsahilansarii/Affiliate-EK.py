import re
import os
import requests

from dotenv import load_dotenv

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)

# =========================================
# LOAD ENV
# =========================================

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
API_TOKEN = os.getenv("API_TOKEN")

# =========================================
# START COMMAND
# =========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [
            InlineKeyboardButton(
                "📢 Updates Channel",
                url="https://t.me/yourchannel"
            )
        ],
        [
            InlineKeyboardButton(
                "💬 Support",
                url="https://t.me/yourusername"
            )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    name = update.effective_user.first_name

    await update.message.reply_text(
        f"""🔥 Welcome {name}

🚀 Convert any shopping or product link into an affiliate link instantly.

📩 Just send your link below.""",
        reply_markup=reply_markup
    )


# =========================================
# URL EXTRACT
# =========================================

def extract_url(text):

    urls = re.findall(r'https?://[^\s]+', text)

    return urls[0] if urls else None


# =========================================
# CONVERT LINK
# =========================================

def convert_link(url):

    api_url = "https://ekaro-api.affiliaters.in/api/converter/public"

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "deal": url,
        "convert_option": "convert_only"
    }

    response = requests.post(
        api_url,
        json=payload,
        headers=headers
    )

    data = response.json()

    if "data" in data:
        return data["data"]

    return None


# =========================================
# MESSAGE HANDLER
# =========================================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = update.message

    text = message.text or message.caption or ""

    if text.startswith("/"):
        return

    original_url = extract_url(text)

    if not original_url:

        await message.reply_text(
            "❌ Please send a valid link."
        )
        return

    processing = await message.reply_text(
        "⚡ Converting your link..."
    )

    try:

        affiliate_link = convert_link(original_url)

        await processing.delete()

        if not affiliate_link:

            await message.reply_text(
                "❌ Failed to convert this link."
            )
            return

        updated_text = text.replace(
            original_url,
            affiliate_link
        )

        keyboard = [
            [
                InlineKeyboardButton(
                    "🚀 Open Link",
                    url=affiliate_link
                )
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        # IMAGE
        if message.photo:

            await context.bot.send_photo(
                chat_id=message.chat.id,
                photo=message.photo[-1].file_id,
                caption=updated_text,
                reply_markup=reply_markup
            )

        # VIDEO
        elif message.video:

            await context.bot.send_video(
                chat_id=message.chat.id,
                video=message.video.file_id,
                caption=updated_text,
                reply_markup=reply_markup
            )

        # DOCUMENT
        elif message.document:

            await context.bot.send_document(
                chat_id=message.chat.id,
                document=message.document.file_id,
                caption=updated_text,
                reply_markup=reply_markup
            )

        # TEXT
        else:

            await message.reply_text(
                updated_text,
                reply_markup=reply_markup
            )

    except Exception as e:

        print(e)

        await processing.delete()

        await message.reply_text(
            "⚠️ Server error. Please try again later."
        )


# =========================================
# MAIN
# =========================================

def main():

    app = Application.builder().token(
        TELEGRAM_TOKEN
    ).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        MessageHandler(
            filters.ALL,
            handle_message
        )
    )

    print("🚀 EarnKro Bot Running...")

    app.run_polling()


if __name__ == "__main__":
    main()
