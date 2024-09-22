from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from config import GH_APP_ID, GH_PRIVATE_KEY, INSTALLATION_ID
from bot.utils.github_auth import create_jwt, get_installation_access_token
from bot.utils.github_search_utils import search_projects_async, format_issue


async def custom_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text.split(',')
    
    language = user_input[0] if user_input[0] != '' else None
    labels = user_input[1:-1] if len(user_input) > 2 else None
    is_good_first_issue = user_input[-1].lower() == 'yes' if len(user_input) > 1 else False
    
    if not GH_APP_ID:
        await update.message.reply_text("GITHUB_APP_ID environment variable is not set")
        return ConversationHandler.END

    jwt_token = create_jwt(GH_APP_ID, private_key_path=GH_PRIVATE_KEY)
    access_token = get_installation_access_token(jwt_token, INSTALLATION_ID)

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
