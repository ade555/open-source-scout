from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import CHOOSING


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [
        [InlineKeyboardButton("Python projects", callback_data='python')],
        [InlineKeyboardButton("JavaScript projects", callback_data='javascript')],
        [InlineKeyboardButton("Documentation projects", callback_data='documentation')],
        [InlineKeyboardButton("Good first issues", callback_data='good_first_issue')],
        [InlineKeyboardButton("Custom search", callback_data='custom')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Welcome to the Open Source Scout! What project would you like to search for?",
        reply_markup=reply_markup
    )
    return CHOOSING
