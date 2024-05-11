import time
import os
import base64
import json

from helpers.auth import token
from helpers.functions import add_items_to_cart

while True:
    print("Waiting for UPC")
    upc = input()
    items = {
        "upc": upc,
        "quantity": 1              
    }
    print(items)
    add_items_to_cart(token, items)