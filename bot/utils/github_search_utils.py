import aiohttp
from cachetools import TTLCache
from bot.utils.github_auth import create_jwt, get_installation_access_token

cache = TTLCache(maxsize=100, ttl=600)


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
