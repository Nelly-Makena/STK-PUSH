import pyqrcode
import datetime
from datetime import datetime
import pytz
import requests
from requests.auth import HTTPBasicAuth
import base64
import json


# Function to generate the QR code
def generate_qr_code(url, filename):
    qr = pyqrcode.create(url)  # Create QR code
    qr.png(filename, scale=10)  # Save as PNG with high resolution
    print(f"QR Code successfully saved as {filename}")


# Function to retrieve access token
def get_access_token():
    consumer_key = "7H7VKVLFzPXAACuGAAA6LJD24D84X98SUGtAL4rWhS2WMIS7"
    consumer_secret = "bLz8mEADcgAbrFv11rjuWkwGXnNaAH1zCsuKBAkMXbrlrXuGhbfROtkZPoL5H7qb"

    api_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    auth = HTTPBasicAuth(consumer_key, consumer_secret)

    response = requests.get(api_url, auth=auth)
    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        print(f"Failed to get access token: {response.text}")
        return None


# Function to initiate STK push
def initiate_stk_push(phone_number, amount):
    access_token = get_access_token()
    if access_token:
        business_short_code = "174379"
        passkey = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
        callback_url = "https://example.com/callback"  #callback URL
        process_request_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

        # Timestamp
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

        # Encode password
        password = base64.b64encode((business_short_code + passkey + timestamp).encode()).decode()

        stk_push_headers = {
            'Authorization': f"Bearer {access_token}",
            'Content-Type': 'application/json',
        }

        stk_push_payload = {
            "BusinessShortCode": business_short_code,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerBuyGoodsOnline",
            "Amount": amount,
            "PartyA": phone_number,
            "PartyB": business_short_code,
            "PhoneNumber": phone_number,
            "CallBackURL": callback_url,
            "AccountReference": "LENGENDARY TABLE",
            "TransactionDesc": " Event Push Test",
        }

        try:
            response = requests.post(process_request_url, headers=stk_push_headers, json=stk_push_payload)
            response.raise_for_status()
            response_data = response.json()
            if response_data.get("ResponseCode") == "0":
                print(f"STK Push sent successfully. CheckoutRequestID: {response_data.get('CheckoutRequestID')}")
            else:
                print(f"STK Push failed: {response_data.get('errorMessage')}")
        except requests.exceptions.RequestException as e:
            print(f"Error sending STK push: {str(e)}")
    else:
        print("Access token not found.")


# Main logic
event_link = "https://forms.gle/dDDh2EChkMcV6VHW9"  # google Form
filename = "event_qr_code.png"  # Desired filename for the QR code
generate_qr_code(event_link, filename)

phone_number = "254757238326"  # My phone Number
amount = 1  # Amount to pay

# Trigger STK push
initiate_stk_push(phone_number, amount)
