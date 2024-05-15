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
current_time = datetime.datetime.now()
customer_auth_code = get_customer_authorization_code(client_id, redirect_uri, scopes, customer_username, customer_password)
token, refresh_token = token, refresh_token = get_customer_access_token(customer_auth_code, encoded_client_token, redirect_uri)

while True:
    # Waits for user input from the UPC scanner
    print("Waiting for UPC")
    upc = input()
    items = {
        "upc": upc,
        "quantity": 1          
    }
   
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
            # Obtains the description, size, and image URL of the product
            description, size, imgurl = get_product_info(product)
            # Standard message for adding something to the cart
            message = f"{description} - {size} has been added to your cart"
            print(message)
           
            break
           
        elif status == 400:
            # User probably left it blank or UPC was not found
            print("Shit's fucked, maybe you left it blank")
           
            break
           
        elif status == 204:
            # Success
            product = get_product(upc, token)
            description, size, imgurl = get_product_info(product)
            message = f"{description} - {size} has been added to your cart"
            print(f'{message}')
            break