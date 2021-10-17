###############################################
#
# Script for control led strips
# through button and mqtt.
#
################################################
#
# Jan Vicha
# 2021
# VER = 10-10-2021
#
################################################

import ntptime
import uasyncio
import ujson
import utime
from machine import PWM, RTC, Pin
from mqtt_as import MQTTClient, config

##### SETTINGS
DEBUG = False
USE_REMOTE_CONTROL = True
BUTTON_PIN = 15
PWM_PIN = 14
GMT = 2
DUTY_LEVELS = [0, 1, 5, 50, 100]
MAX_DUTY = 1023
DELAY_BTN_PRESS = 1000
LED_OFF_HOUR = 23
LED_OFF_MINUTE = 59
##############

with open("config.json") as f:
    CONFIG = ujson.loads(f.read())


class Main:
    """
    Main class for full logic this program.
    Run this class by call 'main'
    """

    def __init__(self):
        # default values
        self.led_off_hour = LED_OFF_HOUR
        self.led_off_minute = LED_OFF_MINUTE
        self.actual_perc_pwm = 0
        self.gmt = GMT

        # inits buttons
        self.button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)
        pin = Pin(PWM_PIN)
        self.pwm = PWM(pin)
        self.pwm.freq(5000)

        self.rtc = RTC()

        # init mqtt client including wifi
        self.config = config
        self.config["subs_cb"] = self.subscribe_mqtt  # subscribe callback
        self.config["connect_coro"] = self.set_subscribe_mqtt  # set subscribed topics
        self.config["server"] = CONFIG["MQTT_IP"]
        self.config["user"] = CONFIG["MQTT_USER"]
        self.config["password"] = CONFIG["MQTT_PASS"]
        self.config["ssid"] = CONFIG["WIFI_SSID"]
        self.config["wifi_pw"] = CONFIG["WIFI_PASSWORD"]
        self.config["keepalive"] = CONFIG["MQTT_KEEPALIVE"]
        self.config["will"] = [
            CONFIG["LW_TOPIC"],
            CONFIG["LW_MSG_OFFLINE"],
            CONFIG["LW_RETAIN"],
            CONFIG["MQTT_QOS"],
        ]
        MQTTClient.DEBUG = DEBUG  # Optional: print diagnostic messages
        self.client = MQTTClient(self.config)

    def btn_check(self):
        """
        Check button if was correctly pressed.
        If yes then call the btn press method.
        If button is pressed longer then DELAY_BTN_PRESS led will be switched off.
        """
        t1 = utime.ticks_ms()
        end = False
        if self.button.value() == 1:
            utime.sleep(0.1)
            # for long btn press turn off
            while self.button.value() == 1:
                if utime.ticks_ms() - t1 > DELAY_BTN_PRESS:
                    self._set_perc_pwm(0)
                    utime.sleep(1)
                    end = True
                    break
            if not end and self.button.value() == 0:
                self._btn_press()
                utime.sleep(0.1)

    def _btn_press(self):
        """
        Emulate press hw button for led.
        Press button is seting sequences of DUTY_LEVELS for control pwm on the led.
        """
        print("Press button")
        for index, level in enumerate(DUTY_LEVELS):
            if self.actual_perc_pwm == level:
                # If last item
                if index + 1 == len(DUTY_LEVELS):
                    self._set_perc_pwm(0)
                else:
                    self._set_perc_pwm(DUTY_LEVELS[index + 1])
                return
        # if value if not in sequence DUTY_LEVES set neighbor value
        near_values = [i for i in DUTY_LEVELS if i > self.actual_perc_pwm]
        if near_values:
            self._set_perc_pwm(min(near_values))
        else:
            self._set_perc_pwm(0)

    def _set_perc_pwm(self, value_percent):
        """
        Set percent power for switch on/off led and publish to mqtt.

        :param int value_percent: Percent value for set pwm power.
        """
        self.actual_perc_pwm = value_percent
        self.pwm.duty(int(MAX_DUTY * value_percent / 100))
        print("Set pwm to: {}".format(value_percent))

    def timer_check(self):
        """
        Check if is time to switch off led.
        """
        local_time = utime.localtime()
        hour = int(local_time[3])
        minute = int(local_time[4])
        sec = int(local_time[5])
        if (
            self.led_off_hour == hour
            and self.led_off_minute == minute
            and sec == 0
            and self.actual_perc_pwm != 0
        ):
            self._set_perc_pwm(0)

    def _decode_bytes(self, value):
        return value.decode("utf-8")

    def subscribe_mqtt(self, topic, msg, retained):
        print("Income msg: ", (topic, msg, retained))
        _topic = self._decode_bytes(topic)
        try:
            # set percent
            if _topic == CONFIG["TOPIC_LED_PERCENT"] and 0 <= int(msg) <= 100:
                self._set_perc_pwm(int(msg))
            # set timer off
            if _topic == CONFIG["TOPIC_LED_TIMER_OFF"] and msg:
                self._set_time_off_from_mqtt(self._decode_bytes(msg))
        except:
            print("Income value error", (topic, msg, retained))

    def _set_time_off_from_mqtt(self, value):
        """
        :param str value: String format like "22:45"
        """
        try:
            _time = value.split(":")
            self.led_off_hour = int(_time[0])
            self.led_off_minute = int(_time[1])
            print("Timer set to: {}:{}".format(self.led_off_hour, self.led_off_minute))
        except:
            print("Bad time format: ", value)

    def _get_timer_off_for_mqtt(self):
        """
        :return: Actual setted timer off for mqtt like "23:00"
        :rtype: str
        """
        return ":".join(
            [
                "{:02d}".format(self.led_off_hour),
                "{:02d}".format(self.led_off_minute),
            ]
        )

    def _set_time(self):
        """
        Synchronize time with ntp and set rtc localtime by setted gmt.
        Call this method after connecting internet.
        """
        for i in range(5):
            utime.sleep(4)
            try:
                ntptime.settime()
                (year, month, mday, hour, minute, second, _, _) = utime.localtime(
                    utime.time() + (3600 * self.gmt)
                )
                self.rtc.datetime((year, month, mday, 0, hour, minute, second, 0))
                print("\nTime setted: {}".format(utime.localtime()))
                break
            except Exception as ex:
                print("\nTime not setted: {}".format(ex))

    async def set_subscribe_mqtt(self, client):
        await client.subscribe(CONFIG["TOPIC_LED_PERCENT"], CONFIG["MQTT_QOS"])
        await client.subscribe(CONFIG["TOPIC_LED_TIMER_OFF"], CONFIG["MQTT_QOS"])

    async def connection_loop(self):
        """
        Loop operating with wifi and mqtt broker.
        """
        while True:
            try:
                value = self.actual_perc_pwm
                timer = self._get_timer_off_for_mqtt()
                await self.client.connect()
                self._set_time()

                # LW message device is online
                await self.client.publish(
                    CONFIG["LW_TOPIC"],
                    CONFIG["LW_MSG_ONLINE"],
                    retain=True,
                    qos=CONFIG["MQTT_QOS"],
                )
                # Led level message
                await self.client.publish(
                    CONFIG["TOPIC_LED_PERCENT_STATUS"],
                    str(self.actual_perc_pwm),
                    retain=True,
                    qos=CONFIG["MQTT_QOS"],
                )
                while True:
                    if value != self.actual_perc_pwm:
                        print(
                            "Publish '{}' to '{}'".format(
                                self.actual_perc_pwm, CONFIG["TOPIC_LED_PERCENT_STATUS"]
                            )
                        )
                        value = self.actual_perc_pwm
                        await self.client.publish(
                            CONFIG["TOPIC_LED_PERCENT_STATUS"],
                            str(self.actual_perc_pwm),
                            retain=True,
                        )

                    if timer != self._get_timer_off_for_mqtt():
                        timer = self._get_timer_off_for_mqtt()
                        print(
                            "Publish '{}' to '{}'".format(
                                timer, CONFIG["TOPIC_LED_TIMER_OFF_STATUS"]
                            )
                        )
                        await self.client.publish(
                            CONFIG["TOPIC_LED_TIMER_OFF_STATUS"], timer, retain=True
                        )

                    await uasyncio.sleep(1)
            except:
                print("Error connect")
                await uasyncio.sleep(30)

    async def btn_loop(self):
        """
        Loop for check HW press button and timer.
        """
        while True:
            self.btn_check()
            self.timer_check()
            await uasyncio.sleep_ms(100)

    async def create_tasks(self):
        loop = uasyncio.get_event_loop()
        if USE_REMOTE_CONTROL:
            loop.create_task(self.connection_loop())
        loop.create_task(self.btn_loop())
        await loop.run_forever()

    def main(self):
        try:
            uasyncio.run(self.create_tasks())
        finally:
            self.client.close()  # Prevent LmacRxBlk:1 errors


if __name__ == "__main__":
    m = Main()
    m.main()
