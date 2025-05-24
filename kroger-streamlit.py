import streamlit as st
# import keyboard
import time
import datetime
import os
import base64
import requests
from functions import get_product, add_items_to_cart, refresh_auth_token, get_product_info, get_customer_access_token, get_customer_authorization_code, add_to_sql
current_time = datetime.datetime.now()
time.sleep(2)
def initialize():
    # keyboard.press_and_release('F11')
    client_id = ""
    client_secret = ""
    customer_username = ""
    customer_password = ""
    redirect_uri = "http://localhost:3000"
    # Defines scopes based on application registration at the Kroger Developers website
    scopes = "cart.basic:write%20product.compact%20profile.compact"
    # Base64 encodes the client_id and client_secret
    encoded_client_token = base64.b64encode(f"{client_id}:{client_secret}".encode('ascii')).decode('ascii')
    # Gets current timestamp
    # Declares the initial set of tokens and auth code. 
    customer_auth_code = get_customer_authorization_code(client_id, redirect_uri, scopes, customer_username, customer_password)
    token, refresh_token = get_customer_access_token(customer_auth_code, encoded_client_token, redirect_uri)
    st.session_state['initialized'] = True
    return token, refresh_token, encoded_client_token

upc = st.text_input("Waiting for UPC")
# left, right = st.columns(2)

#Test UPC ---> 0006414428243 - Rotel Original Diced Tomatoes And Green Chilies

if "initialized" not in st.session_state:
    token, refresh_token, encoded_client_token = initialize()
    
st.session_state['token'] = token
st.session_state['refresh_token'] = refresh_token
st.session_state['encoded_client_token'] =encoded_client_token   


if upc:
    items = {
        "upc": upc,
        "quantity": 1          
    }
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

        st.write(message)
        
    elif status == 400:
        # User probably left it blank or UPC was not found
        st.write("Shit's fucked, maybe you left it blank")
        
        
    elif status == 204:
        # Success
        # try:
        product = get_product(upc, token)
        # print(product)
        description, size, imgurl, brand, category, productId, price_regular, price_promo = get_product_info(product)
        add_to_sql(description, size, imgurl, brand, category, productId, price_regular, price_promo, current_time)
        # Standard message for adding something to the cart
        message = f"{description}, {size}, {brand}, {category}, {productId}, {price_regular}, {price_promo}" + " has been added to your cart"
        st.write(message)
        # except:
            # print("Try again")

# option_map = {
#     0: "Price Check",
#     1: "Add to Cart"
# }
# selection = st.segmented_control(
#     "Tool",
#     options=option_map.keys(),
#     format_func=lambda option: option_map[option],
#     selection_mode="single",
# )


# if left.button("Price Check", use_container_width=True):
#     left.markdown("You clicked the plain button.")
# if right.button("Add to Cart", use_container_width=True):
#     right.markdown("You clicked the Material button.")
