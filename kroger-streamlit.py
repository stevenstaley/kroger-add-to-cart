import datetime
import os
import base64
import requests
from functions import get_product, add_items_to_cart, refresh_auth_token, get_product_info, get_customer_access_token, get_customer_authorization_code, add_to_sql
import keyboard
import time
import streamlit as st

# Create the SQL connection to pets_db as specified in your secrets file.
conn = st.connection('kroger_db', type='sql')
# Stores the "Client ID", "Client Secret", "Customer Username", "Customer Password", and "Redirect URI" as environmental variables for obscurity

client_id = os.environ.get('CLIENT_ID')
client_secret = os.environ.get('CLIENT_SECRET')
customer_username = os.environ.get('CUSTOMER_USERNAME')
customer_password = os.environ.get('CUSTOMER_PASSWORD')
redirect_uri = os.environ.get('REDIRECT_URI')
# Defines scopes based on application registration at the Kroger Developers website
scopes = "cart.basic:write%20product.compact%20profile.compact"
# Base64 encodes the client_id and client_secret
encoded_client_token = base64.b64encode(f"{client_id}:{client_secret}".encode('ascii')).decode('ascii')
# Gets current timestamp
current_time = datetime.datetime.now()
# Declares the initial set of tokens and auth code. 
customer_auth_code = get_customer_authorization_code(client_id, redirect_uri, scopes, customer_username, customer_password)
token, refresh_token = get_customer_access_token(customer_auth_code, encoded_client_token, redirect_uri)



time.sleep(2)
st.text_input("Waiting for UPC")
left, right = st.columns(2)
def initialize():
    keyboard.press_and_release('F11')
    st.session_state['initialized'] = True


if "initialized" not in st.session_state:
    initialize()


if left.button("Price Check", use_container_width=True):
    left.markdown("You clicked the plain button.")
if right.button("Add to Cart", use_container_width=True):
    right.markdown("You clicked the Material button.")

while True:
    # Waits for user input from the UPC scanner
    print("Waiting for UPC")
    upc = input()
    items = {
        "upc": upc,
        "quantity": 1          
    }
    df = conn.query('select * from allitems')
    st.dataframe(df)
    while True:
        status = add_items_to_cart(token, items)
        # Submits the PUT request to add the UPC to the cart
        if status == 401:
            """
            If the access token is expired for 30 minutes, it will throw a 401 error.
            This will use the refresh_auth_token function to request a new access token.
            Once it obtains a new token, it will attempt to add the item to the cart

            Backlog Item - Need to throw the authorization function in this loop so the user
            will not even notice it's renewing.
            """
            token, refresh_token = refresh_auth_token(refresh_token, encoded_client_token)
            # This prints the time the token was renewed just for developer awareness, not needed
            print(f"Refresh token renewed at {current_time}")
            # Adds the item to the cart
            status = add_items_to_cart(token, items)
            # Returns the product JSON
            product = get_product(upc, token)
            # print(product)
            # Obtains the description, size, and image URL of the product
            description, size, imgurl, brand, category, productId, price_regular, price_promo = get_product_info(product)
            add_to_sql(description, size, imgurl, brand, category, productId, price_regular, price_promo, current_time)
            # Standard message for adding something to the cart
            message = f"{description}, {size}, {brand}, {category}, {productId}, {price_regular}, {price_promo}" + " has been added to your cart"

            print(message)
           
            break
           
        elif status == 400:
            # User probably left it blank or UPC was not found
            print("Shit's fucked, maybe you left it blank")
           
            break
           
        elif status == 204:
            # Success
            # try:
            product = get_product(upc, token)
            # print(product)
            description, size, imgurl, brand, category, productId, price_regular, price_promo = get_product_info(product)
            add_to_sql(description, size, imgurl, brand, category, productId, price_regular, price_promo, current_time)
            # Standard message for adding something to the cart
            message = f"{description}, {size}, {brand}, {category}, {productId}, {price_regular}, {price_promo}" + " has been added to your cart"
            print(message)
            # except:
                # print("Try again")
            break



# Potentially good loop to replace the original one 


# while True:
#     upc = input()
#     items = {
#     "upc": upc,
#     "quantity": 1           
#     }
    
#     while True:
#         status = add_items_to_cart(token, items)
        
#         if status == 401:
#             token, refresh_token = refresh_auth_token(refresh_token, encoded_client_token)
#             print(f"Refresh token expired at {current_time}")
#             status = add_items_to_cart(token, items)
#             if status == 401:
#                 print("Getting customer access token, please wait.....")
#                 customer_auth_code = get_customer_authorization_code(client_id, redirect_uri, scopes, customer_username, customer_password)
#                 print("Customer Authorization Code acquired.")
#                 token, refresh_token = get_customer_access_token(customer_auth_code, encoded_client_token, redirect_uri)
#                 print("Token acquired.")
#                 status = add_items_to_cart(token, items)
#                 if status == 201:
#                     product = get_product(upc, token)
#                     description, size, imgurl = get_product_info(product)
#                     message = f"{description} - {size} has been added to your cart @ {imgurl}"
#                     print(message)
                    
#                     break
                    
#                 else:
#                     print(status)
#                     print("Please check your credentials.")
                    
#                 break
                
#             else:
#                 product = get_product(upc, token)
#                 description, size, imgurl = get_product_info(product)
#                 message = f"{description} - {size} has been added to your cart @ {imgurl}"
#                 print(message)
            
#             break
            
#         elif status == 400:
#             print("Shit's fucked, maybe you left it blank")
            
#             break
            
#         elif status == 204:
#             product = get_product(upc, token)
#             print(product)
#             description, size, imgurl = get_product_info(product)
#             message = f"{description} - {size} has been added to your cart @ {imgurl}"
#             print(f'{message}')
#             # inventory.append((description, size, imgurl, 1))
#             break
