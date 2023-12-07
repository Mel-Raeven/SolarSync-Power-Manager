import requests
import json

def authenticate(api_key):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    return headers

def start_miner(farm_id, worker_id, headers):
    url = f'https://api2.hiveos.farm/api/v2/farms/{farm_id}/workers/{worker_id}/actions'
    data = {"action": "start"}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    with open('miner_state.txt', 'w') as f:
        f.write('started')
    return response.json()

def stop_miner(farm_id, worker_id, headers):
    url = f'https://api2.hiveos.farm/api/v2/farms/{farm_id}/workers/{worker_id}/actions'
    data = {"action": "stop"}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    with open('miner_state.txt', 'w') as f:
        f.write('stopped')
    return response.json()