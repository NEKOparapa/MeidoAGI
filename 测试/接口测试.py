import requests
import json

# URL of the API endpoint
url = 'http://localhost:5000/chat'

# Your test message
message = '你不是知道么？'

# Create the data payload
data = {'user_input': message}

# Send the POST request
response = requests.post(url, json=data)

# Print the status code and response text
print("Status code:", response.status_code)
print("Response body:", response.text)