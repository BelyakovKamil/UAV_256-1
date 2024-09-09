import requests

BASE_URL = 'http://127.0.0.1:5000/drones'

def takeoff(drone_id, altitude):
    url = f"{BASE_URL}/{drone_id}/takeoff"
    payload = {"altitude": altitude}
    response = requests.post(url, json=payload)
    return response.json()


if __name__ == '__main__':
    drone_id = "drone_index"
    altitude = 200

    response = takeoff(drone_id, altitude)
    print(f"Ответ от сервера: {response.get('message')}")
