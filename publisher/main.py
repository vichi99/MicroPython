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
import ujson

# MEASURED device - DHT22
# CONFIG["DHT22_PIN"]

# Timezone GMT
# CONFIG["GMT"]

############## SEND DATA INTERVAL #########################
# 1. CHOICE Data meas/send will start in whole minute with zero seconds etc. (12:02:00)
# Set minutes(int) interval for sending data. Higher priority then 2. CHOICE. 
# CONFIG["SYNC_SEND_DATA"]

# 2. CHOICE Data meas/send will ASAP by setted seconds interval(int).
# For using 2. CHOICE you have to set null(in json) to 1. CHOICE
# CONFIG["INTERVAL_SEND_DATA"]
###########################################################


CONFIG = {}

def load_config():
    global CONFIG
    try:
        with open("config.json") as f:
            CONFIG = ujson.loads(f.read())
    except OSError:
        pass


class Main():
    """
    Main class for full logic this program.
    Run this class by call 'main'
    """
    def __init__(self):
        self.wifi = Wifi(ssid=CONFIG["WIFI_SSID"], password=CONFIG["WIFI_PASSWORD"], gmt=CONFIG["GMT"])
        self.mqtt = Mqtt(ip=CONFIG["MQTT_IP"], user=CONFIG["MQTT_USER"], password=CONFIG["MQTT_PASS"])
        self._dht22 = DHT22(Pin(CONFIG["DHT22_PIN"]))


    def _send_data(self):
        """
        Meas dht22 data and publish temperature and humidity via mqtt.
        """
        try:    
            self._dht22.measure() # important for take actual values
            data =  {   "date": localtime(),
                        "temp": str(self._dht22.temperature()),
                        "hum":  str(self._dht22.humidity())
                    }
            data = ujson.dumps(data)
            self.mqtt.publish(CONFIG["DEV_1_TOPIC"], data)
        except Exception as ex:
            print("\t_send_data unable to send `{}`".format(ex))
            pass


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
        
            if CONFIG["SYNC_SEND_DATA"] is not None:
                if second == 0 and minute % CONFIG["SYNC_SEND_DATA"] == 0:
                    # print("\nsending sync data...")
                    self._send_data()
            else:
                if second % CONFIG["INTERVAL_SEND_DATA"] == 0:
                    # print("\nsending interval data...")
                    self._send_data()


if __name__ == "__main__":
    load_config()
    main = Main()
    main.main()
