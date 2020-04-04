###############################################
#
# Script for connecting to wifi, mqqt broker
# and publish measured data from IO to mqtt broker.
#
################################################
#
# Jan Vicha
# 2020
# VER = 4-4-2020
#
################################################


from wifi import Wifi
from mqtt import Mqtt
from dht import DHT22
from machine import Pin
from utime import sleep, localtime

# MEASURED device - DHT22
dht22_pin = 14

# Timezone GMT
GMT = 2

############## SEND DATA INTERVAL #########################
# 1. CHOICE Data meas/send will start in whole minute with zero seconds etc. (12:02:00)
# Set minutes interval for sending data. Higher priority then 2. CHOICE. 
SYNC_SEND_DATA = None

# 2. CHOICE Data meas/send will ASAP by setted seconds interval.
# For using 2. CHOICE you have to set 'None' to 1. CHOICE
INTERVAL_SEND_DATA = 5
###########################################################

# WIFI
WIFI_SSID = ""
WIFI_PASSWORD = ""

# MQTT TOPIC settings.
DEV_NAME = "device_1"
DEV_PLACE = "pokoj"
# MEASURED values topic
TEMP_TOPIC = DEV_NAME + "/" + DEV_PLACE + "/" + "teplota"
HUM_TOPIC = DEV_NAME + "/" + DEV_PLACE + "/" + "vlhkost"

MQTT_IP = ""
MQTT_USER = "test" # optional - depend on mqtt broker
MQTT_PASS = "test" # optional - depend on mqtt broker

class Main():
    """
    Main class for full logic this program.
    Run this class by call 'main'
    """
    def __init__(self):
        self.wifi = Wifi(ssid=WIFI_SSID, password=WIFI_PASSWORD, gmt=GMT)
        self.mqtt = Mqtt(ip=MQTT_IP, user=MQTT_USER, password=MQTT_PASS)
        self._dht22 = DHT22(Pin(dht22_pin))


    def _send_data(self):
        """
        Meas dht22 data and publish temperature and humidity via mqtt.
        """    
        self._dht22.measure() # important for take actual values
        self.mqtt.publish(TEMP_TOPIC, str(self._dht22.temperature()))
        self.mqtt.publish(HUM_TOPIC, str(self._dht22.humidity()))


    # Main loop
    def main(self):
        """
        Main loop.
        """        
        while True:
            sleep(1)

            ######## WIFI CHECK
            if not self.wifi.is_connected():
                self.mqtt.disconnect()
                self.wifi.connect() # infinity loop for connecting to wifi

            ######## MQTT CHECK
            if not self.mqtt.is_connected():
                if not self.mqtt.connect():
                    continue


            ######## INTERVAL & SEND DATA
            minute = localtime()[4]
            second = localtime()[5]
        
            if SYNC_SEND_DATA is not None:
                if second == 0 and minute % SYNC_SEND_DATA == 0:
                    print("\nsending sync data...")
                    print(localtime())
                    # send_data()
            else:
                if second % INTERVAL_SEND_DATA == 0:
                    print("\nsending interval data...")
                    print(localtime())
                    # self._send_data()

def f():
    main = Main()
    main.main()
