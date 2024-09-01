import os
import aiohttp
import requests
from dotenv import load_dotenv
from cachetools import TTLCache
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, ConversationHandler, MessageHandler, filters
from github_auth import create_jwt, get_installation_access_token

load_dotenv()

# States
CHOOSING, TYPING_REPLY = range(2)

cache = TTLCache(maxsize=100, ttl=600) 
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is not set")
private_key_path = os.getenv("GH_PRIVATE_KEY")

async def search_projects_async(session, access_token, language=None, labels=None, is_good_first_issue=False):
    query = "is:open is:issue"
    
    if language:
        query += f" language:{language}"
    
    if labels:
        for label in labels:
            query += f" label:\"{label}\""
    
    if is_good_first_issue:
        query += " label:\"good first issue\""
    
    headers = {
        'Authorization': f'token {access_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    params = {
        'q': query,
        'sort': 'created',
        'order': 'desc'
    }
    if query in cache:
        return cache[query]
    
    async with session.get('https://api.github.com/search/issues', headers=headers, params=params) as response:
    
        if response.status != 200:
            raise Exception(f"Search failed: {response.status}, {response.text}")
        result = await response.json()
        cache[query] = result['items']
        return result['items']

def format_issue(issue):
    return {
        'title': issue['title'],
        'url': issue['html_url'],
        'repository': issue['repository_url'].split('/')[-1],
        'labels': [label['name'] for label in issue['labels']],
        'created_at': issue['created_at'],
    }

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

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    app_id = os.getenv('GH_APP_ID')
    if not app_id:
        await query.edit_message_text("GITHUB_APP_ID environment variable is not set")
        return ConversationHandler.END

    jwt_token = create_jwt(app_id, private_key_path=private_key_path)
    installation_id = os.getenv('INSTALLATION_ID')
    access_token = get_installation_access_token(jwt_token, installation_id)
    await query.edit_message_text(f"Searching for {query.data} projects, please wait...")


    async with aiohttp.ClientSession() as session:
        if query.data == 'custom':
            await query.edit_message_text("Please enter your custom search criteria in the format: language,label1,label2,...,is_good_first_issue\n" "For example: python,documentation,yes")
            return TYPING_REPLY
        else:
            if query.data == 'python':
                results = await search_projects_async(session, access_token, language='python')
            elif query.data == 'javascript':
                results = await search_projects_async(session, access_token, language='javascript')
            elif query.data == 'documentation':
                results = await search_projects_async(session, access_token, labels=['documentation'])
            elif query.data == 'good_first_issue':
                results = await search_projects_async(session, access_token, is_good_first_issue=True)
            
            formatted_results = [format_issue(issue) for issue in results[:5]]  # Limit to 5 results
        
        if not formatted_results:
            await query.edit_message_text("No results found.")
        else:
            response = "Here are some projects you might be interested in:\n\n"
            for result in formatted_results:
                response += f"• {result['title']}\n"
                response += f"  Repository: {result['repository']}\n"
                response += f"  URL: {result['url']}\n"
                response += f"  Labels: {', '.join(result['labels'])}\n"
                response += f"  Created at: {result['created_at']}\n\n"
            
            await query.edit_message_text(response)
        
        return ConversationHandler.END

async def custom_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text.split(',')
    
    language = user_input[0] if user_input[0] != '' else None
    labels = user_input[1:-1] if len(user_input) > 2 else None
    is_good_first_issue = user_input[-1].lower() == 'yes' if len(user_input) > 1 else False

    app_id = os.getenv('GH_APP_ID')
    if not app_id:
        await update.message.reply_text("GITHUB_APP_ID environment variable is not set")
        return ConversationHandler.END

    jwt_token = create_jwt(app_id, private_key_path=private_key_path)
    installation_id= os.getenv('INSTALLATION_ID')
    access_token = get_installation_access_token(jwt_token, installation_id)

    results = search_projects_async(access_token, language, labels, is_good_first_issue)
    formatted_results = [format_issue(issue) for issue in results[:5]]  # Limit to 5 results
    
    if not formatted_results:
        await update.message.reply_text("No results found.")
    else:
        response = "Here are some projects you might be interested in:\n\n"
        for result in formatted_results:
            response += f"• {result['title']}\n"
            response += f"  Repository: {result['repository']}\n"
            response += f"  URL: {result['url']}\n"
            response += f"  Labels: {', '.join(result['labels'])}\n"
            response += f"  Created at: {result['created_at']}\n\n"
        
        await update.message.reply_text(response)
    
    return ConversationHandler.END

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