import httpx
import json

def test_read_products():
    url = "http://127.0.0.1:8000/products/"
    params = {"limit": 1000}
    try:
        response = httpx.get(url, params=params)
        print(f"Products Status Code: {response.status_code}")
        if response.status_code == 422:
            print(f"Products Error Detail: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

def test_get_movements():
    url = "http://127.0.0.1:8000/movements/"
    params = {"limit": 500}
    try:
        response = httpx.get(url, params=params)
        print(f"Movements Status Code: {response.status_code}")
        if response.status_code == 422:
            print(f"Movements Error Detail: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_read_products()
    test_get_movements()
