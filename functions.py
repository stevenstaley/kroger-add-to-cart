import requests
import json

def add_items_to_cart(token, items):
    """ Adds specified items to users shopping cart
    Arguments:
        items {array[dict]} -- Array of item dictionaries with keys "upc" and "quantity"
    """
    url = 'https://api.kroger.com/v1/cart/add'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    }
    data = {'items': [items]}

    response = requests.put(url, headers=headers, data=json.dumps(data))
    if 200 <= response.status_code < 300:
        print("Successfully added items to cart")
    else:
        print("Something went wrong, items may not have been added to card (status code: %s)" %response.status_code)
        print(response.json())