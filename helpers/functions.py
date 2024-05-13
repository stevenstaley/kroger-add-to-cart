import requests
import json
import os
import base64
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

client_id = os.environ.get('CLIENT_ID')
client_secret = os.environ.get('CLIENT_SECRET')
customer_username = os.environ.get('CUSTOMER_USERNAME')
customer_password = os.environ.get('CUSTOMER_PASSWORD')
redirect_uri = os.environ.get('REDIRECT_URI')
scopes = "cart.basic:write%20product.compact%20profile.compact"
encoded_client_token = base64.b64encode(f"{client_id}:{client_secret}".encode('ascii')).decode('ascii')

def add_items_to_cart(token, items):
    url = 'https://api.kroger.com/v1/cart/add'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    }
    data = {'items': [items]}

    response = requests.put(url, headers=headers, data=json.dumps(data))
    return response.status_code


def get_customer_authorization_code(client_id, redirect_uri, scopes, customer_username, customer_password):
    AUTH_URL = f"https://api.kroger.com/v1/connect/oauth2/authorize?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope={scopes}"
    chrome_options = Options()  
    chrome_options.add_argument("--headless")
    driver = Chrome(executable_path="C:/Users/steven.w.staley/Desktop/chromedriver_linux64/chromedriver.exe", options=chrome_options)
    url = AUTH_URL.format(client_id=client_id, redirect_uri=redirect_uri)

    # Go to the authorization url, enter username and password and submit
    driver.get(url)
    username = driver.find_elements('username')
    username.send_keys(customer_username)
    password = driver.find_elements('password')
    password.send_keys(customer_password)
    driver.find_elements('signin_button').click()
     
    try:
        auth_button = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.ID, "authorize")))
        if auth_button:
            auth_button.click()
    except:
        pass
   
    uri = driver.current_url

    return uri.split("code=")[1]


def get_customer_access_token(encoded_client_token, redirect_uri, customer_username, customer_password):
    customer_auth_code = get_customer_authorization_code(customer_username, customer_password)
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
    return token, refresh_token

def get_product_info(product):
    newest = product['data']
    item = newest['items']
    description = newest['description']
    size = item[0]['size']
    images = newest['images']
    imgurl = ""
    for p in images:
        if p['perspective'] == "front":
            sizes = p['sizes']
            for i in sizes:
                if i['size'] == "large":
                    imgurl = i['url']
    return description, size, imgurl


def get_product(upc, token):
    search = {
        "productId": upc,
        "upc": upc
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    }
    product = requests.get(f"https://api.kroger.com/v1/products/{upc}", headers=headers, data=search)
    json = product.json()

    return json

def refresh_auth_token(refresh_token, encoded_client_token):
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