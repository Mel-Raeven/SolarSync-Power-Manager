import time
import os
from ics2000.Core import *
from HiveOS.Core import *
from envLoader import loadEnvFile


def main():
  loadEnvFile()

  hub = Hub(os.environ.get("MACADRESS"), os.environ.get("EMAIL"), os.environ.get("PASSWORD"))

  api_key = os.environ.get("HIVEOS_API_KEY")
  farm_id = os.environ.get("HIVEOS_FARM_ID")
  worker_id = os.environ.get("HIVEOS_WORKER_ID")
  worker_consumption = os.environ.get("WORKER_CONSUMPTION")

  headers = authenticate(api_key)

  p1_module = None
  for i in hub.devices():
    print("%s -> %s" % (i.name(), hub.get_device_status(i)))
    if i.name() == "P1 Module":
      p1_module = i._id

  try:
    current = hub.get_device_check(p1_module)
    if len(current) > 5:
      timestr = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
      consumption = int(current[4])
      production  = int(current[5])
      
      print("%s : Consumption %d W - Production %d W" % (timestr, consumption, production))
      
      if production - consumption >= worker_consumption:
        try:
            with open('miner_state.txt', 'r') as f:
                state = f.read().strip()
        except FileNotFoundError:
            state = 'stopped'
        if state == 'started':
            start_miner(farm_id, worker_id, headers)
        elif state == 'stopped':
            stop_miner(farm_id, worker_id, headers)
    else:
      print("reply too short")
  except Exception as e:
    print("something went really wrong")
    print(e)

if __name__ == "__main__":
  main()