import requests
import json
import os

def authenticate(api_key):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    return headers

def start_miner(hub, hub_id):
    hub.turnon(hub_id)
    with open('miner_state.txt', 'w') as f:
        f.write('started')

def stop_miner(farm_id, worker_id, headers):
    farm_id = os.environ.get("HIVEOS_FARM_ID")
    worker_id = os.environ.get("HIVEOS_WORKER_ID")
    url = f'https://api2.hiveos.farm/api/v2/farms/{farm_id}/workers/{worker_id}/command'
    data = {'command': 'shutdown'}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    with open('miner_state.txt', 'w') as f:
        f.write('stopped')
    return response.json()

def miner_state(farm_id, headers):
    farm_id = os.environ.get("HIVEOS_FARM_ID")
    url = f'https://api2.hiveos.farm/api/v2/farms/{farm_id}/workers'
    response = requests.get(url, headers=headers)
    data = response.json()
    stats = bool(data['data'][0]['stats']['online'])
    return stats
