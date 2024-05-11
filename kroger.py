import time
import os
import base64
import json

from helpers.auth import get_customer_access_token, get_customer_authorization_code
from helpers.functions import add_items_to_cart

print(token)

while True:
    print("Waiting for UPC")
    upc = input()
    items = {
        "upc": upc,
        "quantity": 1              
    }
    print(items)
    add_items_to_cart(token, items)