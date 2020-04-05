# Utils scripts
Scripts for servicing main scripts.


# WIFI class

It is very simple class created for my own purposes.
Class obtain connecting to wifi and set time by ntp.

- `init` input arg:
```python
    def __init__(self, ssid, password, gmt):
        """
        Init class variable, rtc instance, disconnect wifi and set wifi to active.
        :param ssid: ssid name of wifi to connect
        :type ssid: str
        :param password: wifi password
        :type password: str
        :param gmt: timezone
        :type gmt: int
        """        
        self._ssid = ssid
        self._password = password
        self._gmt = gmt 
        self.con_wifi = network.WLAN(network.STA_IF)
        self._reload(True)
        self._rtc = RTC()
```

Make network instance, disconnect from some wifi and set active wifi on True. Make rtc instance.

- `connect` It is connecting infinity loop. After successfully connected load ntp time and set into rtc datetime.

- `disconnect` Disconnect wifi and set active wifi on False.

- `is_connected` Return bool state if device is connected to wifi.

# MQTT class

It is very simple class created for my own purposes.
Class obtain connecting to mqtt broker with option publishing data.

- `init` make mqtt client instance, disconnect from some mqqt broker.

```python
    def __init__(self, ip, user="", password=""):
        client_id = ubinascii.hexlify(machine.unique_id())
        self._mqtt = MQTTClient(client_id=client_id, server=ip, user=user, password=password)
        self.disconnect()
```

- `connect` Once connecting shot. Return True if connecting was successfully.

- `disconnect` Disconnect mqtt client.

- `is_connected` Return bool state if device is connected mqtt broker.

- `publish` Sending message data to current topic. This function is useful for check connection, too. Return True if data was corrected sended.



