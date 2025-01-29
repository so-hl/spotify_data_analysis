import requests
import os
from dotenv import load_dotenv
import base64


# Load environment variables from .env file
load_dotenv()

# Define Spotify credentials
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")


# Function to retrieve token
def get_token():
    # Ensure client_id and client_secret are valid strings
    if not CLIENT_ID or not CLIENT_SECRET:
        raise ValueError("Provide client_id and client_string in .env")

    # Create the base64-encoded authorisation string
    auth_string = CLIENT_ID + ":" + CLIENT_SECRET
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")

    # Set up the token request URL and headers
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
    }
    
    # Prepare the data for the request
    data = {"grant_type": "client_credentials"}
    
    # Make the POST request to get the token
    response = requests.post(url, headers=headers, data=data)
    
    # Check for a successful response
    if not response.ok:
        raise Exception(f"Failed to retrieve token. Status code: {response.status_code}, Response: {response.json()}")
    
    access_token = response.json().get('access_token')

    return {
        "Authorization": f"Bearer {access_token}"
    }

if __name__ == '__main__':
    print(get_token())