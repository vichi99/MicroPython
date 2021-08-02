# This file is executed on every boot (including wake-boot from deepsleep)
import uos, machine, time, ntptime, ujson
import gc

try:
  import usocket as socket
except:
  import socket

from machine import Pin
import network

import esp
esp.osdebug(None)

gc.collect()

from wifi import Wifi

with open("config.json") as f:
    CONFIG = ujson.loads(f.read())

wifi_net = Wifi(
  ssid=CONFIG["WIFI_SSID"],
  password=CONFIG["WIFI_PASSWORD"],
  gmt=CONFIG["GMT"],
)
def local_network():
  global wifi_net
  if not wifi_net.is_connected():
    print(wifi_net.is_connected())
    wifi_net.connect(loop=False)
  else:
    print(wifi_net.is_connected())


def acecss_point_network():
  ssid = 'LED-M'
  password = '123456789'

  ap = network.WLAN(network.AP_IF)
  ap.active(True)
  ap.config(essid=ssid, password=password)

  while ap.active() == False:
    time.sleep(1)
    pass

  print('AP created successfully')
  print(ap.ifconfig())

  # https://randomnerdtutorials.com/esp32-esp8266-micropython-web-server/