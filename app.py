from telegram import BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters
from config import TOKEN, CHOOSING, TYPING_REPLY, WEBHOOK_URL, PORT
from bot.handlers.start_handler import start
from bot.handlers.button_handler import button
from bot.handlers.custom_search_handler import custom_search
import asyncio

def main() -> None:
    webhook_url=f"{WEBHOOK_URL}/{TOKEN}"
    application = Application.builder().token(TOKEN).build()
    commands = [
        BotCommand(command="start", description="Start interacting with the bot"),
    ]
    application.bot.set_my_commands(commands)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [CallbackQueryHandler(button)],
            TYPING_REPLY: [MessageHandler(filters.TEXT & ~filters.COMMAND, custom_search)],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    application.add_handler(conv_handler)

    application.bot.set_webhook(url=webhook_url)

    # use this locally
    # application.run_polling()
    
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=webhook_url
    )

if __name__ == '__main__':
    main()