import requests
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

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