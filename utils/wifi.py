import network, ntptime
from utime import sleep, time, localtime
from machine import RTC


class Wifi:
    """
    class obtain connecting to wifi and update rtc time by ntptime and gmt.
    """

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

    def _set_time(self):
        """
        synchronize time with ntp and set rtc localtime by setted gmt.
        """
        for i in range(5):
            sleep(4)
            try:
                ntptime.settime()
                (year, month, mday, hour, minute, second, weekday, yearday) = localtime(
                    time() + (3600 * self._gmt)
                )
                self._rtc.datetime((year, month, mday, 0, hour, minute, second, 0))
                print("\nTime setted: {}".format(localtime()))
                break
            except Exception as ex:
                print("\nTime not setted: {}".format(ex))

    def _reload(self, set_active):
        """
        Disconnect wifi if is connected and set active by input arg.
        :param set_active: set active wifi status
        :type set_active: bool
        """
        if self.con_wifi.isconnected():
            self.con_wifi.disconnect()
        self.con_wifi.active(set_active)

    def connect(self,sleep_time=10, infinity_loop=True):
        """
        Loop for connecting to wifi.
        If successfull then return.

        :param sleep_time: timeout at while loop defaults to 10
        :type sleep_time: int, optional
        :param infinity_loop: set infinite while loop, defaults to True
        :type infinity_loop: bool, optional
        """
        self._reload(True)
        self.con_wifi.connect(self._ssid, self._password)
        print("Wifi:")
        if infinity_loop:
            while not self.is_connected():
                print("\twifi connecting...")
                sleep(sleep_time)
            print("\twifi connected -config: {}".format(self.con_wifi.ifconfig()))
            self._set_time()
        else:
            sleep(sleep_time)
            if self.is_connected():
                print("\twifi connected -config: {}".format(self.con_wifi.ifconfig()))
                self._set_time()
            else:
                print("\twifi not connected -config: {}".format(self.con_wifi.ifconfig()))

    def disconnect(self):
        """
        Disconnect wifi and set active to False.
        """
        self._reload(False)
        print("Wifi: disconected")

    def is_connected(self):
        """
        :return: return True if wifi is connected
        :rtype: bool
        """
        return self.con_wifi.isconnected()
