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
  worker_consumption = int(os.environ.get("WORKER_CONSUMPTION"))
  kaku_plug_id = int(os.environ.get("KAKU_PLUG_ADRESS"))

  headers = authenticate(api_key)

  p1_module = None
  
  # Get all devices
  for i in hub.devices():
    print("%s -> %s" % (i.name(), hub.get_device_status(i)))
    if i.name() == "P1 Module":
      p1_module = i._id
  

  # Main logic
  try:
    current = hub.get_device_check(p1_module)
    if len(current) > 5:
      # Get the current production and consumption
      consumption = int(current[4])
      production  = int(current[5])
      total_usage = production - consumption
      
      # Calculate the total availabilty
      total_availabilty = total_usage - worker_consumption
      
      # Get the current state of the miner
      state = miner_state(farm_id, headers)

      # If the total availabilty is positive, start the miner
      if total_availabilty >= 0:
        print("Hit power trigger")
        # If the miner is already started, do nothing
        if state == True:
          print("miner already started")

        # If the miner is stopped, start it  
        else:
          print("starting miner")
          start_miner(hub, kaku_plug_id)
      
      # If the total availabilty is negative, stop the miner
      else:
        if state == True:
          print("stopping miner, not enough power")
          stop_miner(farm_id, worker_id, headers)

          print("waiting 20 seconds for the miner to power down")
          time.sleep(20)
          
          print("turning off KaKu plug")
          hub.turnoff(kaku_plug_id)
        else:
          print("doing nothing, miner already stopped and not enough power")

    # If the data is not available, do nothing
    else:
      print("not getting p1 data")
  
  # If something goes wrong, do nothing
  except Exception as e:
    print("something went really wrong")
    print(e)

if __name__ == "__main__":
  main()