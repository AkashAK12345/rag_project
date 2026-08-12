import urllib.request
import json
import time

url = f"http://localhost:8000/api/v1/forecast/dashboard?t={time.time()}"
try:
    with urllib.request.urlopen(url) as response:
        print(response.read().decode("utf-8"))
except Exception as e:
    print(f"Error: {e}")
