import os
import requests
from requests.auth import HTTPBasicAuth

# Récupérer la clé API et autres informations nécessaires
MTN_API_USER = os.getenv("MTN_API_USER")
MTN_API_KEY = os.getenv("MTN_API_KEY")
MTN_SUBSCRIPTION_KEY = os.getenv("MTN_SUBSCRIPTION_KEY")

def get_mtn_access_token_api():
    url = "https://proxy.momoapi.mtn.com/collection/token/"
    headers = {
        "Ocp-Apim-Subscription-Key": MTN_SUBSCRIPTION_KEY,
    }

    # Faire un appel POST pour obtenir le token
    response = requests.post(url, headers=headers, auth=HTTPBasicAuth(MTN_API_USER, MTN_API_KEY))

    # Vérifier la réponse de l'API
    if response.status_code == 200:
        token_data = response.json()
        return token_data.get("access_token")
    else:
        print(f"Échec de la connexion. Code d'erreur : {response.status_code}")
        print(response.text)
        return None

# # Appel de la fonction pour récupérer le token
# access_token = get_mtn_access_token_api()
# print(f"Access Token : {access_token}")
