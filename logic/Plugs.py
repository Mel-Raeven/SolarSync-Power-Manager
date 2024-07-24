from logic.KaKuConnector import KaKuHubConnector, KaKuPlugs
import json

def get_added_devices():
    with open(file='config/app-settings.json') as file:
            devices = json.load(file)
    return devices

def ListPlugs():
    devices = get_added_devices()
    if any(hub.get("Device") == "KaKu" for hub in devices["Hubs"]):
        return ListKakuPlugs() 

def StartPlugs(capacity):
    devices = get_added_devices()
    remaining_capacity = capacity
    if any(hub.get("Device") == "KaKu" for hub in devices["Hubs"]):
        plugs = ListKakuPlugs()
        sorted_plugs = sorted(plugs, key=lambda plug: plug.get("Priority"))
        for plug in sorted_plugs:
            if remaining_capacity >= plug.get("usage"):
                start_plug(plug)
                remaining_capacity -= plug.get("usage")

def start_plug(plug):
    if plug.get("type") == "KaKu":
        hub = KaKuHubConnector()
        hub.turnon(plug.get("Id"))

def ListKakuPlugs():
    hub = KaKuHubConnector()
    plugs: list = KaKuPlugs(hub=hub)
    plugs_json = json.dumps({"plugs": plugs})
    with open(file='config/found-plugs.json', mode='w') as file:
        file.write(plugs_json)
    return plugs