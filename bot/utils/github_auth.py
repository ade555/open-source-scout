import os
import jwt
import time
import requests
from dotenv import load_dotenv

load_dotenv()


app_id = os.getenv('GH_APP_ID')
private_key_path = os.getenv("GH_PRIVATE_KEY")
installation_id= os.getenv('INSTALLATION_ID')


def create_jwt(app_id, private_key_path):
    with open(private_key_path, 'rb') as key_file:
        private_key = key_file.read()
    
    payload = {
        'iat': int(time.time()),
        'exp': int(time.time()) + (10 * 60),
        'iss': app_id
    }
    
    return jwt.encode(payload, private_key, algorithm='RS256')



def get_installation_id(jwt_token):
    """
    helper function to get an installation ID. You will typically only need to run this once.
    """
    
    headers = {
         'Authorization': f'Bearer {jwt_token}',
         'Accept': 'application/vnd.github.v3+json'
    }
    response = requests.get(
         'https://api.github.com/app/installations',
         headers=headers
    )
    if response.status_code != 200:
        raise Exception(f"Failed to get installations: {response.status_code}, {response.text}")
    
    installations = response.json()
    if not installations:
        raise Exception("No installations found for this GitHub App")
    
    return installations[0]['id']



def get_installation_access_token(jwt_token, installation_id):
    headers = {
        'Authorization': f'Bearer {jwt_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    response = requests.post(
        f'https://api.github.com/app/installations/{installation_id}/access_tokens',
        headers=headers
    )
    return response.json()['token']
