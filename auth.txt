def get_customer_access_token(customer_auth_code, encoded_client_token, redirect_uri):
    url = 'https://api.kroger.com/v1/connect/oauth2/token'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f'Basic {encoded_client_token}',
    }
    auth_payload = {
        'grant_type':"authorization_code",
        'code': customer_auth_code,
        'redirect_uri': redirect_uri,
    }
    response = requests.post(url, headers=headers, data=auth_payload)
    token = json.loads(response.text).get('access_token')
    refresh_token = json.loads(response.text).get('refresh_token')
    # Outputs the access token and refresh token
    # The access token is only good for 1800 seconds (30 minutes)
    # The refresh token is good for 6 months. When the access token expires, the refresh token is used to obtain a new 30 minute access token.
    return token, refresh_token