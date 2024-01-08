import requests
from requests.sessions import session

# URL of your Flask application
base_url = 'http://127.0.0.1:5000'

# Start a session
with requests.Session() as s:
    # Simulate a login
    login_url = f'{base_url}/login'
    login_data = {
        'username': 'pop',  # Replace with your username
        'password': '1'   # Replace with your password
    }
    login_response = s.post(login_url, data=login_data)

    # Check if login was successful
    if login_response.ok:
        # Make a request to your API endpoint
        api_url = f'{base_url}/api/get_user'
        api_params = {'user_id': 6}  # Replace 3 with the desired user_id
        response = s.get(api_url, params=api_params)

        if response.ok:
            # Process the response
            user_data = response.json()
            print(user_data)
        else:
            print(f"Error: {response.text}")
    else:
        print("Login failed")
