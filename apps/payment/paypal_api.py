import requests
from .paypal_config import PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET, PAYPAL_API_BASE

def get_access_token():
    response = requests.post(f'{PAYPAL_API_BASE}/v1/oauth2/token', 
                             headers={'Accept': 'application/json', 'Accept-Language': 'en_US'}, 
                             auth=(PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET), 
                             data={'grant_type': 'client_credentials'})
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        raise Exception('Failed to retrieve access token')
