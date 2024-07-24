from logic.KaKuConnector import KaKuHubConnector, KaKuP1
from logic.Plugs import StartPlugs
import json

def scan_power():
    while True:
        # Read the JSON file
        with open('config/app-settings.json') as file:
            data = json.load(file)

        # Get the value of the p1-provider field
        p1_provider = data['P1-provider']

        if p1_provider == 'KaKu':
            StartPlugs(KaKuPower())

def KaKuPower():
    hub = KaKuHubConnector()
    p1_module = KaKuP1(hub)

    current = hub.get_device_check(p1_module)
    return int(current[5])

