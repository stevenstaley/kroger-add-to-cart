import requests
import datetime
import os
import base64
from functions import get_product, add_items_to_cart, refresh_auth_token, get_product_info, get_customer_access_token, get_customer_authorization_code

client_id = os.environ.get('CLIENT_ID')
client_secret = os.environ.get('CLIENT_SECRET')
customer_username = os.environ.get('CUSTOMER_USERNAME')
customer_password = os.environ.get('CUSTOMER_PASSWORD')
redirect_uri = os.environ.get('REDIRECT_URI')
scopes = "cart.basic:write%20product.compact%20profile.compact"
encoded_client_token = base64.b64encode(f"{client_id}:{client_secret}".encode('ascii')).decode('ascii')

url = f'https://api.kroger.com/v1/connect/oauth2/authorize?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope={scopes}'
print(url)
current_time = datetime.datetime.now()
customer_auth_code = get_customer_authorization_code(client_id, redirect_uri, scopes, customer_username, customer_password)
token, refresh_token = token, refresh_token = get_customer_access_token(customer_auth_code, encoded_client_token, redirect_uri)

print(token)
print('-------------')
print(refresh_token)



while True:
   
    print("Waiting for UPC")
    upc = input()
    items = {
    "upc": upc,
    "quantity": 1          
    }
   
    # while True:
    status = add_items_to_cart(token, items)
    print(status)
    
       
#         if status == 401:
#             token, refresh_token = refresh_auth_token(refresh_token, encoded_client_token)
#             print(f"Refresh token renewed at {current_time}")
#             status = add_items_to_cart(token, items)
#             product = get_product(upc, token)
#             description, size, imgurl = get_product_info(product)
#             message = f"{description} - {size} has been added to your cart"
           
#             break
           
#         elif status == 400:
#             print("Shit's fucked, maybe you left it blank")
           
#             break
           
#         elif status == 204:
#             product = get_product(upc, token)
#             description, size, imgurl = get_product_info(product)
#             message = f"{description} - {size} has been added to your cart"
#             print(f'{message}')
#             # inventory.append((description, size, imgurl, 1))
#             break
           
# # #     # df = pd.DataFrame(inventory, columns=['Item', 'Size', 'Image', 'Quantity'])

# # # # def send_pushover(message, img):
# # # #     r = requests.post("https://api.pushover.net/1/messages.json", data = {
# # # #       "token": "APP_TOKEN",
# # # #       "user": "USER_KEY",
# # # #       "message": message
# # # #     },
# # # #     files = {
# # # #       "attachment": ("image.jpg", open(img, "rb"), "image/jpeg")
# # # #     })
