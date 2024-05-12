import time
import os
import base64
import json
import requests
from .helpers.functions import add_items_to_cart

client_id = os.environ.get('CLIENT_ID')
client_secret = os.environ.get('CLIENT_SECRET')
customer_username = os.environ.get('CUSTOMER_USERNAME')
customer_password = os.environ.get('CUSTOMER_PASSWORD')
redirect_uri = os.environ.get('REDIRECT_URI')
scopes = "cart.basic:write%20product.compact%20profile.compact"
encoded_client_token = base64.b64encode(f"{client_id}:{client_secret}".encode('ascii')).decode('ascii')
customer_auth_code = os.environ.get('KROGER_CUST_AUTH_CODE')

token_url = 'https://api.kroger.com/v1/connect/oauth2/token'
headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Authorization': f'Basic {encoded_client_token}',
}
payload = {
    'grant_type':"authorization_code",
    'code': customer_auth_code,
    'redirect_uri': redirect_uri,
}
response = requests.post(token_url, headers=headers, data=payload)
token = json.loads(response.text).get('access_token')

while True:
    print("Waiting for UPC")
    upc = input()
    items = {
        "upc": upc,
        "quantity": 1              
    }
    add_items_to_cart(token, items)
