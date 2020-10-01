###############################################
#
# Script for connecting to wifi, mqqt broker
# and publish measured data from IO to mqtt broker.
#
################################################
#
# Jan Vicha
# 2020
# VER = 29-9-2020
#
################################################


from wifi import Wifi
from mqtt import Mqtt
from dht import DHT22
from machine import Pin
from utime import sleep, localtime, ticks_diff, ticks_ms, sleep_ms
import ujson

######## DATA FORMAT
### format sended values dict as string
# data = {
#             "name": CONFIG["NAME_DEVICE"],
#             "position": CONFIG["POSITION"],
#             "date": local_time,
#             "temperature": float,
#             "humidity": float
#         }


# MEASURED device - DHT22
# CONFIG["DHT22_PIN"]

# Timezone GMT
# CONFIG["GMT"]

############## SEND DATA INTERVAL #########################
# 1. Set true if you will wait to synchronize on whole minute with zero seconds etc. (12:02:00).
# If false meas will start immediately.
# CONFIG["SYNC_SEND_DATA"]

# 2. Setted interval(int) sending data.
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


class Main:
    """
    Main class for full logic this program.
    Run this class by call 'main'
    """

    def __init__(self):
        self.wifi = Wifi(
            ssid=CONFIG["WIFI_SSID"],
            password=CONFIG["WIFI_PASSWORD"],
            gmt=CONFIG["GMT"],
        )
        self.mqtt = Mqtt(
            ip=CONFIG["MQTT_IP"],
            user=CONFIG["MQTT_USER"],
            password=CONFIG["MQTT_PASS"],
        )
        self.dht22 = DHT22(Pin(CONFIG["DHT22_PIN"]))
        self.is_sending_synchronizate = False

    def _send_data(self):
        """
        Meas dht22 data and publish temperature and humidity via mqtt.
        """
        try:
            local_time = localtime()[:-2] # remove mili and micro seconds
            self.dht22.measure()  # important for take actual values
            data = {
                "name": CONFIG["NAME_DEVICE"],
                "position": CONFIG["POSITION"],
                "date": local_time,
                "temperature": str(self.dht22.temperature()),
                "humidity": str(self.dht22.humidity()),
            }
            data = ujson.dumps(data)
            self.mqtt.publish(CONFIG["DEV_TOPIC"], data)
        except Exception as ex:
            print("\t_send_data unable to send `{}`".format(ex))
            pass

    # Main loop
    def main(self):
        """
        Main loop.
        """
        start = ticks_ms()
        first_start = True # defined for timing interval
        while True:
            sleep_ms(50)
            ######## WIFI CHECK
            if not self.wifi.is_connected():
                self.is_sending_synchronizate = False
                self.mqtt.disconnect()
                self.wifi.connect()  # infinity loop for connecting to wifi

            ######## MQTT CHECK
            if not self.mqtt.is_connected():
                self.is_sending_synchronizate = False
                if not self.mqtt.connect():
                    sleep(10)
                    continue

            ######## INTERVAL & SEND DATA
            
            ### check sending data with synchro time
            if CONFIG["SYNC_SEND_DATA"]:
                # if synchronizate sending setted
                # waiting on whole minute with 0 seconds
                if not self.is_sending_synchronizate:
                    second = localtime()[5]
                    if second != 0:
                        # if not synchronizated
                        continue
                    self.is_sending_synchronizate = True

            #### Sending data 
            # timing sending data this way is not the best solution
            # if you want excelent timig. Find better solution.
            diff = ticks_diff(ticks_ms(), start) # ms
            if first_start or diff >= CONFIG["INTERVAL_SEND_DATA"] * 1000:
                first_start = False
                start = ticks_ms()
                self._send_data()




if __name__ == "__main__":
    load_config()
    main = Main()
    main.main()
