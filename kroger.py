import time
import os
import base64
import json
import requests
client_id = os.environ.get('CLIENT_ID')
client_secret = os.environ.get('CLIENT_SECRET')
customer_username = os.environ.get('CUSTOMER_USERNAME')
customer_password = os.environ.get('CUSTOMER_PASSWORD')
redirect_uri = os.environ.get('REDIRECT_URI')
scopes = "cart.basic:write%20product.compact%20profile.compact"
encoded_client_token = base64.b64encode(f"{client_id}:{client_secret}".encode('ascii')).decode('ascii')

customer_auth_code = os.environ.get('KROGER_CUST_AUTH_CODE')

print(customer_auth_code)
print(client_id)

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

def add_items_to_cart(token, items):
    """ Adds specified items to users shopping cart
    Arguments:
        items {array[dict]} -- Array of item dictionaries with keys "upc" and "quantity"
    """
    url = 'https://api.kroger.com/v1/cart/add'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    }
    data = {'items': [items]}

    response = requests.put(url, headers=headers, data=json.dumps(data))
    if 200 <= response.status_code < 300:
        print("Successfully added items to cart")
    else:
        print("Something went wrong, items may not have been added to card (status code: %s)" %response.status_code)
        print(response.json())

while True:
    print("Waiting for UPC")
    upc = input()
    items = {
        "upc": upc,
        "quantity": 1              
    }
    print(items)
    add_items_to_cart(token, items)
