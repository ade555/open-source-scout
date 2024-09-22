import aiohttp
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from config import GH_APP_ID, GH_PRIVATE_KEY, INSTALLATION_ID, TYPING_REPLY
from bot.utils.github_auth import create_jwt, get_installation_access_token
from bot.utils.github_search_utils import search_projects_async, format_issue


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    if not GH_APP_ID:
        await query.edit_message_text("GITHUB_APP_ID environment variable is not set")
        return ConversationHandler.END

    jwt_token = create_jwt(GH_APP_ID, private_key_path=GH_PRIVATE_KEY)
    access_token = get_installation_access_token(jwt_token, INSTALLATION_ID)
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

