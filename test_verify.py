import requests
import json
import time
import os

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

    reports_to_upload = [
        "data/WorkLocationReport.xls_080526060115AM950.xlsx",
        "data/RawMaterial_Report_2026_05_08_11_18_47.xlsx"
    ]

    for report_path in reports_to_upload:
        if os.path.exists(report_path):
            print(f"\n2. Ingesting {report_path}...")
            with open(report_path, "rb") as f:
                resp = requests.post(f"{BASE_URL}/ingestion", files={"file": (os.path.basename(report_path), f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}, headers=headers)
            print("Ingestion response:", resp.status_code, resp.text)
        else:
            print(f"Skipping {report_path}, not found.")
            
    # Give the index a second to settle if it's asynchronous, though it should be sync.
    time.sleep(2)

    print("\n3. Testing Analytics Dashboard...")
    resp = requests.get(f"{BASE_URL}/analytics/dashboard", headers=headers)
    print("Analytics response:", resp.status_code)
    try:
        data = resp.json()
        print(f"Analytics overview: {json.dumps(data.get('overview', {}), indent=2)}")
        if "charts" in data:
            for chart_name, chart_data in data["charts"].items():
                print(f"  Chart {chart_name}: {len(chart_data.get('data', []))} data points")
    except Exception as e:
        print(f"Failed to parse analytics response: {e}, {resp.text}")

    print("\n4. Testing Forecast Dashboard...")
    resp = requests.get(f"{BASE_URL}/forecast/dashboard", headers=headers)
    print("Forecast response:", resp.status_code)
    try:
        data = resp.json()
        print(f"Forecast overview: {json.dumps(data.get('overview', {}), indent=2)}")
        if "charts" in data:
            for chart_name, chart_data in data["charts"].items():
                print(f"  Chart {chart_name}: {len(chart_data.get('data', []))} data points")
    except Exception as e:
        print(f"Failed to parse forecast response: {e}, {resp.text}")

if __name__ == "__main__":
    main()
