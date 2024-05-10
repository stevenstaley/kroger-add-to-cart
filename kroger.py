import time
import os
import base64
import json

from helpers.auth import get_customer_access_token, get_customer_authorization_code
# encoded_client_token, customer_auth_code, client_id, client_secret, customer_password, customer_username

from helpers.functions import add_items_to_cart
client_id = os.environ.get('CLIENT_ID')
client_secret = os.environ.get('CLIENT_SECRET')
customer_username = os.environ.get('CUSTOMER_USERNAME')
customer_password = os.environ.get('CUSTOMER_PASSWORD')
redirect_uri = os.environ.get('REDIRECT_URI')
scopes = "cart.basic:write%20product.compact%20profile.compact"
encoded_client_token = base64.b64encode(f"{client_id}:{client_secret}".encode('ascii')).decode('ascii')
customer_auth_code = get_customer_authorization_code(client_id, redirect_uri, customer_username, customer_password, scopes)
token = get_customer_access_token(encoded_client_token, customer_auth_code, redirect_uri)
print(customer_auth_code)
print(token)

while True:
    print("Waiting for UPC")
    upc = input()
    items = {
        "upc": upc,
        "quantity": 1              
    }
    print(items)
    add_items_to_cart(token, items)