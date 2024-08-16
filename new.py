import datetime
import os
import base64
from functions import get_product, add_items_to_cart, refresh_auth_token, get_product_info, get_customer_access_token, get_customer_authorization_code

# Stores the "Client ID", "Client Secret", "Customer Username", "Customer Password", and "Redirect URI" as environmental variables for obscurity
# client_id = os.environ.get('cloud-api-new-83f6f015f2a66f9c328f8eefe6f5abfe5066498447986739229')
client_id = 'cloud-api-new-83f6f015f2a66f9c328f8eefe6f5abfe5066498447986739229'
client_secret = '1HF1vXQlZa0uyw73PlC-6-ZAlIKoRhZUpLdfPfrX'
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
            product = get_product(upc, token)
            description, size, imgurl, brand, category, productId = get_product_info(product)
            message = f"{description} - {size} - {brand} - {category} - {productId} has been added to your cart"
            print(f'{message}')
            print(product)
            print('401')
            break
           
        elif status == 400:
            # User probably left it blank or UPC was not found
            print("Shit's fucked, maybe you left it blank")
           
            break
           
        elif status == 204:
            product = get_product(upc, token)
            description, size, imgurl, brand, category, productId = get_product_info(product)
            message = f"{description} - {size} - {brand} - {category} - {productId} has been added to your cart"
            print(f'{message}')
            print(product)
            break



# while True:
# #     # Waits for user input from the UPC scanner
#     print("Waiting for UPC")
#     upc = input()
#     # token = 'eyJhbGciOiJSUzI1NiIsImprdSI6Imh0dHBzOi8vYXBpLmtyb2dlci5jb20vdjEvLndlbGwta25vd24vandrcy5qc29uIiwia2lkIjoiWjRGZDNtc2tJSDg4aXJ0N0xCNWM2Zz09IiwidHlwIjoiSldUIn0.eyJhdWQiOiJjbG91ZC1hcGktbmV3LTgzZjZmMDE1ZjJhNjZmOWMzMjhmOGVlZmU2ZjVhYmZlNTA2NjQ5ODQ0Nzk4NjczOTIyOSIsImV4cCI6MTcyMzQwMzcxMCwiaWF0IjoxNzIzNDAxOTA1LCJpc3MiOiJhcGkua3JvZ2VyLmNvbSIsInN1YiI6ImJlN2VkN2FlLThkNTctNDYyYi1iZTE1LTA1YmUzMjEwMDM2NiIsInNjb3BlIjoiY2FydC5iYXNpYzp3cml0ZSBwcm9kdWN0LmNvbXBhY3QgcHJvZmlsZS5jb21wYWN0IiwiYXV0aEF0IjoxNzIzNDAxOTEwNTM5MTU4MDY3LCJwZmN4IjoidXJuOmtyb2dlcmNvOnByb2ZpbGU6c2hvcHBlcjoxOWFkYTQ1NS0xMzg0LWQ1MWEtN2Y3NS1kZWVlMzBjOTNlM2EiLCJhenAiOiJjbG91ZC1hcGktbmV3LTgzZjZmMDE1ZjJhNjZmOWMzMjhmOGVlZmU2ZjVhYmZlNTA2NjQ5ODQ0Nzk4NjczOTIyOSJ9.IBUFwg1uaTyn814wdIm84vQC8B8MVV-_2rQPYduIDd5WW8A_jg54jPhibZAHDzxlPKpvN5Nf1DSqrN_GLdBEWM3YHSp80ZL5oJgT4GFAgeAr16GDEkxPqxZrDFXwMMZIFRFX0X90nx4MRzx6EjlfjeHNdmA4kF2MayfjH5HvsMId74WHCuZL_gK7Ztb3PxMsfSgwt9C1ODb6o5uGL6UCJddBcfpUj098rMZe0-y97EQtNbPMEYK6MYtx-OgT26il0E-kJToMCuc-0S7lL95tuDnYa4bWYL8RvvLUGV1QrpG7VL1Vp2tiBVQfAG2zSs_yFiyFiaf4l7xWkOY3Wm9h6w'
#     while True:
#         product = get_product(upc, token)
#         description, size, imgurl, brand, category, productId = get_product_info(product)
#         message = f"{description} - {size} - {brand} - {category} - {productId} has been added to your cart"
#         print(f'{message}')
#         print(product)
#         break


    # 0001111011968
    # 0001111011968

#{'data': {'productId': '0001111011968', 'upc': '0001111011968', 'productPageURI': '/p/kroger-tomato-paste/0001111011968?cid=dis.api.tpi_products-api_20240521_b:all_c:p_t:cloud-api-new-83f6f0', 'aisleLocations': [], 'brand': 'Kroger', 'categories': ['Canned & Packaged'], 'countryOrigin': 'UNITED STATES', 'description': 'Kroger® Tomato Paste', 'images': [{'perspective': 'left', 'sizes': [{'size': 'xlarge', 'url': 'https://www.kroger.com/product/images/xlarge/left/0001111011968'}, {'size': 'large', 'url': 'https://www.kroger.com/product/images/large/left/0001111011968'}, {'size': 'medium', 'url': 'https://www.kroger.com/product/images/medium/left/0001111011968'}, {'size': 'small', 'url': 'https://www.kroger.com/product/images/small/left/0001111011968'}, {'size': 
# 'thumbnail', 'url': 'https://www.kroger.com/product/images/thumbnail/left/0001111011968'}]}, {'perspective': 'right', 'sizes': [{'size': 'xlarge', 'url': 
# 'https://www.kroger.com/product/images/xlarge/right/0001111011968'}, {'size': 'large', 'url': 'https://www.kroger.com/product/images/large/right/0001111011968'}, {'size': 'medium', 'url': 'https://www.kroger.com/product/images/medium/right/0001111011968'}, {'size': 'small', 'url': 'https://www.kroger.com/product/images/small/right/0001111011968'}, {'size': 'thumbnail', 'url': 'https://www.kroger.com/product/images/thumbnail/right/0001111011968'}]}, {'perspective': 'front', 'featured': True, 'sizes': [{'size': 'xlarge', 'url': 'https://www.kroger.com/product/images/xlarge/front/0001111011968'}, {'size': 'large', 'url': 'https://www.kroger.com/product/images/large/front/0001111011968'}, {'size': 'medium', 'url': 'https://www.kroger.com/product/images/medium/front/0001111011968'}, {'size': 'small', 'url': 'https://www.kroger.com/product/images/small/front/0001111011968'}, {'size': 'thumbnail', 'url': 'https://www.kroger.com/product/images/thumbnail/front/0001111011968'}]}], 'items': [{'itemId': '0001111011968', 'favorite': False, 'fulfillment': {'curbside': False, 
# 'delivery': False, 'inStore': False, 'shipToHome': False}, 'size': '12 oz'}], 'itemInformation': {}, 'temperature': {'indicator': 'Ambient', 'heatSensitive': False}}}


