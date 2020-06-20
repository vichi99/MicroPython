# Description

- Main script publishing by wifi measured data from `Nodemcu` via MicroPython to mqtt broker.
- After successfully connect to wifi is setted rtc time by ntp.
- Measured data are temperature and humidity by using `DHT22` sensor.
- Interval sending measured can be synchronize on zero seconds by minutes or interval is setted by second and sending is ASAP.
- Script operate with my [utils classes](https://github.com/vichi99/ESP8266/tree/master/utils) `mqtt` and `wifi`.

# Installation

- Connecting with device and deploying scripts is described [here.](https://github.com/vichi99/ESP8266/blob/master/Deploy_MicroPython_scripts.md)

- For this application we need load this files to device. Utils are available [here.](https://github.com/vichi99/ESP8266/tree/master/utils)

- Make config file.
```
boot.py
main.py
config.json
../utils/mqtt.py
../utils/wifi.py
```

# Usage

- Before runing scripts is important make `config.json` from `config.json.example` and fill it.
```python
"DHT22_PIN": 14

# Timezone
"GMT": 2

############## SEND DATA INTERVAL #########################
# 1. CHOICE Data meas/send will start in whole minute with zero seconds etc. (12:02:00)
# Set minutes interval for sending data. Higher priority then 2. CHOICE. 
"SYNC_SEND_DATA": 1,

# 2. CHOICE Data meas/send will ASAP by setted seconds interval.
# For using 2. CHOICE you have to set 'None' to 1. CHOICE
"INTERVAL_SEND_DATA": null

"WIFI_SSID": ""
"WIFI_PASSWORD": ""
"DEV_1_TOPIC": "pokoj/device_1/data"
"MQTT_IP": ""
"MQTT_USER": "" # optional - depend on mqtt broker
"MQTT_PASS": "" # optional - depend on mqtt broker
```
On this picture below is shown logic this code.

![main_diagram](docs/main_diagram.jpg)



