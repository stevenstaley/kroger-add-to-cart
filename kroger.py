import requests
import simple_cache
import base64
import json
import pandas as pd
import datetime
from functions import get_product, add_items_to_cart, refresh_auth_token, get_product_info, get_customer_access_token, encoded_client_token, redirect_uri, customer_username, customer_password, additme

current_time = datetime.datetime.now()

token, refresh_token = get_customer_access_token(encoded_client_token, redirect_uri, customer_username, customer_password)

while True:
    upc = input()
    items = {
    "upc": upc,
    "quantity": 1          
    }
   
    while True:
        status = add_items_to_cart(token, items)
       
        if status == 401:
            token, refresh_token = refresh_auth_token(refresh_token, encoded_client_token)
            print(f"Refresh token expired at {current_time}")
            status = add_items_to_cart(token, items)
            product = get_product(upc, token)
            description, size, imgurl = get_product_info(product)
            message = f"{description} - {size} has been added to your cart"
           
            break
           
        elif status == 400:
            print("Shit's fucked, maybe you left it blank")
           
            break
           
        elif status == 204:
            product = get_product(upc, token)
            description, size, imgurl = get_product_info(product)
            message = f"{description} - {size} has been added to your cart"
            print(f'{message}')
            # inventory.append((description, size, imgurl, 1))
            break
           
    # df = pd.DataFrame(inventory, columns=['Item', 'Size', 'Image', 'Quantity'])


# In[61]:


# df = pd.DataFrame(inventory, columns=['Item', 'Size', 'Image', 'Quantity'])


# In[ ]:


def send_pushover(message, img):
    r = requests.post("https://api.pushover.net/1/messages.json", data = {
      "token": "APP_TOKEN",
      "user": "USER_KEY",
      "message": message
    },
    files = {
      "attachment": ("image.jpg", open(img, "rb"), "image/jpeg")
    })


# In[ ]:


# from PIL import Image
# import requests
# from io import BytesIO

# def image_get(imgurl):
#     response = requests.get(imgurl)
#     img = Image.open(BytesIO(response.content))
#     return img


# In[ ]:


# img = image_get(imgurl)
