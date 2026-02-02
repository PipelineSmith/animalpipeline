import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import logging
import asyncio
from dotenv import load_dotenv
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes

from openaigenerator.animalfacts.impl import generate_cute_post

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
)

# Async post generator
async def post_to_telegram_async():
    result = generate_cute_post()
    if not result:
        logging.warning("No content generated.")
        return

    # Expecting: animal, text, image_path
    try:
        animal, text, image_path = result
    except ValueError:
        logging.error("generate_cute_post() must return (animal, text, image_path)")
        return

    bot = Bot(token=TOKEN)

    caption = f"🐾 {str(animal).capitalize()} says:\n\n{text}"

    try:
        # Send photo with caption
        if image_path and os.path.exists(image_path):
            with open(image_path, "rb") as f:
                await bot.send_photo(
                    chat_id=CHAT_ID,
                    photo=f,
                    caption=caption
                )
        else:
            # Fallback: send text only
            await bot.send_message(
                chat_id=CHAT_ID,
                text=caption
            )

        logging.info("Posted to Telegram.")

    except Exception as e:
        logging.error(f"Telegram send failed: {e}")

    finally:
        # Cleanup temp image file
        if image_path and os.path.exists(image_path):
            try:
                os.remove(image_path)
                logging.info(f"Deleted temp image: {image_path}")
            except Exception as e:
                logging.warning(f"Failed to delete temp image {image_path}: {e}")


# Manual trigger via /test command
async def handle_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await post_to_telegram_async()
    await update.message.reply_text("Cute animal post triggered!")


# Manual run (optional utility)
def post_to_telegram():
    asyncio.run(post_to_telegram_async())


def start_command_listener():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("test", handle_test))
    logging.info("Telegram command listener started.")
    app.run_polling()
