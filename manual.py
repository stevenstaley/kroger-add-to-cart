#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
import json
import time
import datetime
import os
import base64
import subprocess
import sqlite3
import pandas as pd
from sqlalchemy import create_engine


# In[ ]:


def get_customer_access_token(customer_auth_code, encoded_client_token, redirect_uri):
    url = 'https://api.kroger.com/v1/connect/oauth2/token'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f'Basic {encoded_client_token}',
    }
    auth_payload = {
        'grant_type':"authorization_code",
        'code': customer_auth_code,
        'redirect_uri': redirect_uri,
    }
    response = requests.post(url, headers=headers, data=auth_payload)
    token = json.loads(response.text).get('access_token')
    refresh_token = json.loads(response.text).get('refresh_token')
    # Outputs the access token and refresh token
    # The access token is only good for 1800 seconds (30 minutes)
    # The refresh token is good for 6 months. When the access token expires, the refresh token is used to obtain a new 30 minute access token.
    return token, refresh_token

############################################################
#            Refresh The 30 MInute Access Token            #
############################################################
def refresh_auth_token(refresh_token, encoded_client_token):
    # Takes the refresh token and does a POST request to obtain a new 30 minute access token
    url = 'https://api.kroger.com/v1/connect/oauth2/token'
    refresh_payload = {
    'grant_type':"refresh_token",
    'refresh_token': refresh_token
    }
    headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Authorization': f'Basic {encoded_client_token}'
    }
    refresh_response = requests.post(url, headers=headers, data=refresh_payload)
    token = json.loads(refresh_response.text).get('access_token')
    refresh_token = json.loads(refresh_response.text).get('refresh_token')
    return token, refresh_token

############################################################
#              Add To Cart Function                        #
############################################################
def add_items_to_cart(token, items):
    # Conducts a PUT request using the 30 minute access token and the item information
    url = 'https://api.kroger.com/v1/cart/add'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    }
    data = {'items': [items]}
    response = requests.put(url, headers=headers, data=json.dumps(data))
    #submits a PUT request to add the item to the cart and returns the status code to determine if the operation was a success
    return response.status_code

############################################################
#               Get Product Function                       #
############################################################
def get_product(upc, token):
    # Takes the upc of the scanned product and the access token in order to run the GET request
    search = {
        "productId": upc,
        "upc": upc
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    }
    product = requests.get(f"https://api.kroger.com/v1/products/{upc}", headers=headers, params=search)
    json = product.json()
    # Returns the JSON for the product information which is broken out by the get_product_info function
    return json

############################################################
#               Get Product Information                    #
############################################################
def get_product_info(product):
    # product is the json returning from the get product function
    # Isolates the data key
    newest = product['data']
    # Declares the product description
    try:
        description = newest['description']
    except:
        description = "No Description Found"
    try:
        brand = newest['brand']
    except:
        brand = "No Brand Found"
    try:
        category = newest['categories']
    except:
        category = "No Category Found"
    try:
        productId = newest['productId']
    except:
        productId = "No UPC Found"
    # Declares the product size
    try:
        size = newest['items'][0]['size']
    except:
        size = "No Size Found"
    # Locates the images asssociated with the product
    try:
        images = newest['images']
        imgurl = ""
        # Locates the url for the 'large' size image of the product.
        for p in images:
            if p['perspective'] == "front":
                sizes = p['sizes']
                for i in sizes:
                    if i['size'] == "large":
                        imgurl = i['url']
    except:
        images = 'No images found'
    return description, size, imgurl, brand, category, productId


# In[ ]:


client_id = 'cloud-api-new-83f6f015f2a66f9c328f8eefe6f5abfe5066498447986739229'
client_secret = '1HF1vXQlZa0uyw73PlC-6-ZAlIKoRhZUpLdfPfrX'
customer_username = os.environ.get('CUSTOMER_USERNAME')
customer_password = os.environ.get('CUSTOMER_PASSWORD')
redirect_uri = "http://localhost:3000/callback"
# Defines scopes based on application registration at the Kroger Developers website
scopes = "cart.basic:write%20product.compact%20profile.compact"
# Base64 encodes the client_id and client_secret
encoded_client_token = base64.b64encode(f"{client_id}:{client_secret}".encode('ascii')).decode('ascii')
# Gets current timestamp
current_time = datetime.datetime.now()
# Declares the initial set of tokens and auth code. 

link = f"https://api.kroger.com/v1/connect/oauth2/authorize?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope={scopes}"
print(link)


# In[ ]:


customer_auth_code = input()
token, refresh_token = get_customer_access_token(customer_auth_code, encoded_client_token, redirect_uri)


# In[ ]:


print(token)
print(refresh_token)


# In[ ]:


# token = 'eyJhbGciOiJSUzI1NiIsImprdSI6Imh0dHBzOi8vYXBpLmtyb2dlci5jb20vdjEvLndlbGwta25vd24vandrcy5qc29uIiwia2lkIjoiWjRGZDNtc2tJSDg4aXJ0N0xCNWM2Zz09IiwidHlwIjoiSldUIn0.eyJhdWQiOiJjbG91ZC1hcGktbmV3LTgzZjZmMDE1ZjJhNjZmOWMzMjhmOGVlZmU2ZjVhYmZlNTA2NjQ5ODQ0Nzk4NjczOTIyOSIsImV4cCI6MTcyMzczODA2MywiaWF0IjoxNzIzNzM2MjU4LCJpc3MiOiJhcGkua3JvZ2VyLmNvbSIsInN1YiI6ImJlN2VkN2FlLThkNTctNDYyYi1iZTE1LTA1YmUzMjEwMDM2NiIsInNjb3BlIjoiY2FydC5iYXNpYzp3cml0ZSBwcm9kdWN0LmNvbXBhY3QgcHJvZmlsZS5jb21wYWN0IiwiYXV0aEF0IjoxNzIzNzM2MjYzMDk2MDEwNTEwLCJwZmN4IjoidXJuOmtyb2dlcmNvOnByb2ZpbGU6c2hvcHBlcjoxOWFkYTQ1NS0xMzg0LWQ1MWEtN2Y3NS1kZWVlMzBjOTNlM2EiLCJhenAiOiJjbG91ZC1hcGktbmV3LTgzZjZmMDE1ZjJhNjZmOWMzMjhmOGVlZmU2ZjVhYmZlNTA2NjQ5ODQ0Nzk4NjczOTIyOSJ9.kRYnKKx-ib9mxOQs_954KOT7Niza-FhXEmQFsDUlzdDWE_eCdrZ2_6XOejiAqkJ2Or17YmbMEtCowri8XcjrqlBF1nOTKAOD50AEkVGzr08xyuyivRYgvnSWnEy0060CLB_S_ivjVBXEVcTSQl3GvHx4IN7ORq6PSSD_NUIf4ONmoewCqfpkvvPCAx37Ikl7g5hlu1KaL1k6Yj-XNnX2Y3a-7pQ0I6bSRDnAbHdMAKZByROcU8XhZO2RTfuFgtGuaN4NvDuE9B1IHMughIJM3bN53qf40qCZQyWa27FcDKXHkTLSdz_wQBcv6HjdQBLeWVpP6UG4m8VNLO_PfvW_CQ'
# # refresh_token = 'vSajI_kOWU8ecJ1V3NBgxgNzfDtWQhDYzfCkrEQc'


# In[ ]:


while True:
    # Waits for user input from the UPC scanner
    print("Waiting for UPC")
    upc = input()
    items = {
        "upc": upc,
        "quantity": 1          
    }
    product = get_product(upc, token)
    description, size, imgurl, brand, category, productId = get_product_info(product)
    message = f"{description} - {size} - {brand} - {category} - {productId} has been added to your cart"
    # print(f'{message}')
    # print(product)
    with sqlite3.connect("kroger1234.db") as db: 
        cursor = db.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS cart1 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description MEDIUMTEXT,
            size MEDIUMTEXT,
            brand MEDIUMTEXT,
            category MEDIUMTEXT,
            productId MEDIUMTEXT)
        ''')
        cursor.execute('INSERT INTO cart1 (description, size, brand, category, productId) VALUES (?, ?, ?, ?, ?)', [description, size, brand, str(category), productId])            
         # Commit your changes in the database
        db.commit()
        # data=cursor.execute('''SELECT * FROM cart1''') 
        # for row in data: 
        #     print(row)


# In[2]:


cnx = create_engine('sqlite:///kroger1234.db').connect()
sql = pd.read_sql('cart1', cnx)
sql


# In[ ]:
