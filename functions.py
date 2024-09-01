import requests
import json
import time
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import sqlite3
current_time = datetime.datetime.now()

############################################################
#    Get Customer Authorization Code For Specific Cart     #
############################################################
def get_customer_authorization_code(client_id, redirect_uri, scopes, customer_username, customer_password):
    # Uses Selenium to open the browser to the authentication URL 
    service = Service(executable_path=r"C:\Users\kelly\Downloads\Python\Kroger\kroger-add-to-cart\chromedriver.exe")
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
    time.sleep(1)
    # Find the username input
    username = driver.find_element(By.ID, 'username')
    # Inputs customer username
    username.send_keys(customer_username)
    time.sleep(1)
    # Finds the password input
    password = driver.find_element(By.ID, 'password')
    # Inputs customer password
    password.send_keys(customer_password)
    time.sleep(1)
    # Finds the sign in button
    button = driver.find_element(By.ID, 'signin_button')
    time.sleep(1)
    # Submits the authorization with the username and password
    button.click()
    # If that specific customer has already authorized, it will skip this try loop
    try:
        auth_button = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.ID, "authorize")))
        if auth_button:
            auth_button.click()
    except:
        pass
    time.sleep(2)
    uri = driver.current_url
    # Returns string after '{redirect_uri}/code=' which is the customer_auth_code required to get an access token
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
        "upc": upc,
        # In order to get prices, you have to include the filter.locationId parameter in the request. 
        "filter.locationId": "01100644"
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
        category = newest['categories'][0]
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
    try:
        price = newest['items'][0]['price']['regular']
    except:
        price = "No price found"
    try:
        promo_price = newest['items'][0]['price']['promo']
    except:
        promo_price = 0
    # Locates the images asssociated with the product
    try:
        images = newest['images']
        imgurl = ""
        # Locates the url for the 'large' size image of the product.
        for p in images:
            if p['perspective'] == "front":
                sizes = p['sizes']
                for i in sizes:
                    if i['size'] == "thumbnail":
                        imgurl = i['url']
    except:
        images = 'No images found'
    try:
        price_regular = newest['items'][0]['price']['regular']
    except:
        price_regular = 0
    try:
        price_promo = newest['items'][0]['price']['promo']
    except:
        price_promo = 0
    return description, size, imgurl, brand, category, productId, price_regular, price_promo


def add_to_sql(description, size, imgurl, brand, category, productId, price_regular, price_promo, current_time):
    with sqlite3.connect("kroger.db") as db: 
        cursor = db.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS allitems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description MEDIUMTEXT,
            size MEDIUMTEXT,
            brand MEDIUMTEXT,
            category MEDIUMTEXT,
            image MEDIUMTEXT,
            productId MEDIUMTEXT,
            price REAL,
            promoprice REAL,
            datetime TIMESTAMP)
        ''')
        cursor.execute('INSERT INTO allitems (description, size, brand, category, image, productId, price, promoprice, datetime) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', [description, size, brand, str(category), imgurl, productId, price_regular, price_promo, current_time])            
#          # Commit your changes in the database
        db.commit()
    


# def get_location(token, zip_code):
#     # Takes the upc of the scanned product and the access token in order to run the GET request
#     headers = {
#         'Content-Type': 'application/json',
#         'Authorization': f'Bearer {token}',
#     }
#     product = requests.get(f"https://api.kroger.com/v1/locations?filter.zipCode.near={zip_code}", headers=headers)
#     json = product.json()
#     # Returns the JSON for the product information which is broken out by the get_product_info function
#     return json

# zip_code = "#####"
# data = get_location(token, zip_code)
# print(data)