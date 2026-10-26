"""Send six requests through Kong; the sixth should receive HTTP 429."""
import httpx

url = "http://127.0.0.1:8000/api/orders"
with httpx.Client(timeout=5) as client:
    for number in range(1, 7):
        response = client.get(url)
        print(f"Request {number}: HTTP {response.status_code}; "
              f"remaining={response.headers.get('RateLimit-Remaining', 'n/a')}")
