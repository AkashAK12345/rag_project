import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"
ADMIN_USER = "admin"
ADMIN_PASS = "changeme123"

def main():
    print("1. Logging in...")
    resp = requests.post(f"{BASE_URL}/auth/login", json={"username": ADMIN_USER, "password": ADMIN_PASS})
    if resp.status_code != 200:
        print("Login failed", resp.text)
        return
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    print("2. Creating dummy report...")
    csv_content = "business_domain,content,reporting_period\nSALES,\"This report is about Q3 sales performance. Sales grew by 20%.\",Q3 2023\n"
    with open("dummy_report.csv", "w", encoding="utf-8") as f:
        f.write(csv_content)

    print("3. Ingesting report...")
    with open("dummy_report.csv", "rb") as f:
        resp = requests.post(f"{BASE_URL}/ingestion", files={"file": ("dummy_report.csv", f, "text/csv")}, headers=headers)
    print("Ingestion response:", resp.status_code, resp.text)

    print("4. Querying without restarting...")
    payload = {"question": "What is this report about?", "stream": False}
    resp = requests.post(f"{BASE_URL}/query", json=payload, headers=headers)
    print("Query response:", resp.status_code, resp.text)

if __name__ == "__main__":
    main()
