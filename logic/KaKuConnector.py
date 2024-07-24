from envLoader import loadEnvFile
from ics2000.Core import *
import os
import json

def KaKuHubConnector():
    loadEnvFile()

    hub = Hub(os.environ.get("KAKUMACADRESS"), os.environ.get("KAKUEMAIL"), os.environ.get("KAKUPASSWORD"))
    return hub

def KaKuPlugs(hub) -> str:
    plugs = []
    for i in hub.devices():
        plug = {
            "type": "KaKu",
            "name": i.name(),
            "id": i.id()
        }
        plugs.append(plug)
    return json.dumps(plugs)

def KaKuP1(hub):
    p1_module = None

    for i in hub.devices():
        print("%s -> %s" % (i.name(), hub.get_device_status(i)))
        if i.name() == "P1 Module":
            p1_module = i._id
    return p1_module