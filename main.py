import time
import os
from ics2000.Core import *
from envLoader import loadEnvFile


def main():
  loadEnvFile()
  hub = Hub(os.environ.get("MACADRESS"), os.environ.get("EMAIL"), os.environ.get("PASSWORD"))

  p1_module = None
  for i in hub.devices():
    print("%s -> %s" % (i.name(), hub.get_device_status(i)))
    if i.name() == "P1 Module":
      p1_module = i._id


  while(True):
    try:
      current = hub.get_device_check(p1_module)
      if len(current) > 5:
        timestr = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        consumption = int(current[4])
        production  = int(current[5])
        print("%s : Consumption %d W - Production %d W" % (timestr, consumption, production))

      else:
        print("reply too short")
    except Exception as e:
      print("something went really wrong")
      print(e)
      pass
    time.sleep(10)

if __name__ == "__main__":
  main()