import requests
import json
import time
import base64
import os
import subprocess
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

client_id = os.environ.get('CLIENT_ID')
client_secret = os.environ.get('CLIENT_SECRET')
customer_username = os.environ.get('CUSTOMER_USERNAME')
customer_password = os.environ.get('CUSTOMER_PASSWORD')
redirect_uri = os.environ.get('REDIRECT_URI')
scopes = "cart.basic:write%20product.compact%20profile.compact"
encoded_client_token = base64.b64encode(f"{client_id}:{client_secret}".encode('ascii')).decode('ascii')
service = Service(executable_path=r"C:\Users\kelly\Downloads\Python\Kroger\helpers\chromedriver.exe")
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
driver = Chrome(service=service, options=chrome_options)

while True:
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
    customer_auth_code = uri.split("code=")[1]

    subprocess.run(['setx', 'KROGER_CUST_AUTH_CODE', customer_auth_code], shell=True)
    print(customer_auth_code)
