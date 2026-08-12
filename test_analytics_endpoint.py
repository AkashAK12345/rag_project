"""Quick test to verify analytics/forecast dashboard endpoints return chart data."""
import json
import urllib.request

def test_endpoint(url, name):
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read().decode())
            print(f"\n=== {name} ===")
            if "charts" in data:
                for chart_name, chart_data in data["charts"].items():
                    count = len(chart_data.get("data", []))
                    status = "✅" if count > 0 else "❌"
                    print(f"  {status} {chart_name}: {count} data points")
            if "overview" in data:
                print(f"\nOverview: {json.dumps(data['overview'], indent=2)}")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_endpoint("http://localhost:8000/api/v1/analytics/dashboard", "Analytics Dashboard")
    test_endpoint("http://localhost:8000/api/v1/forecast/dashboard", "Forecast Dashboard")
