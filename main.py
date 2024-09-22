from telegram import BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters
from config import TOKEN, CHOOSING, TYPING_REPLY
from bot.handlers.start_handler import start
from bot.handlers.button_handler import button
from bot.handlers.custom_search_handler import custom_search

def main() -> None:
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

    application.run_polling()

if __name__ == '__main__':
    main()