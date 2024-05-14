import requests
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

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
    service = Service(executable_path=r"C:\Users\kelly\Downloads\Python\Kroger\add-to-cartV1\chromedriver.exe")
    chrome_options = Options()  
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-features=SameSiteByDefaultCookies")
    chrome_options.add_argument("start-maximized")
    chrome_options.add_experimental_option("prefs", {"profile.default_content_settings.cookies": 1, "profile.block_third_party_cookies": False})
    chrome_options.add_argument('log-level=3')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    AUTH_URL = f"https://api.kroger.com/v1/connect/oauth2/authorize?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope={scopes}"

    url = AUTH_URL.format(client_id=client_id, redirect_uri=redirect_uri, scopes=scopes)
    # Go to the authorization url, enter username and password and submit
    driver.get(url)
    time.sleep(2)
    username = driver.find_element(By.ID, 'username')
    username.send_keys(customer_username)
    time.sleep(1)
    password = driver.find_element(By.ID, 'password')
    password.send_keys(customer_password)
    time.sleep(1)
    button = driver.find_element(By.ID, 'signin_button')
    time.sleep(1)
    button.click()

    try:
        auth_button = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.ID, "authorize")))
        if auth_button:
            auth_button.click()
    except:
        pass
    time.sleep(2)
    uri = driver.current_url
    return uri.split("code=")[1]

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