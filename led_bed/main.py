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

import utime
from machine import PWM, Pin

##### SETTINGS
BUTTON_PIN = 15
PWM_PIN = 14
DUTY_LEVELS = [0, 1, 5, 50, 100]
MAX_DUTY = 1023
DELAY_BTN_PRESS = 1000
##############

class Main:
    """
    Main class for full logic this program.
    Run this class by call 'main'
    """

    def __init__(self):
        # default values
        self.actual_perc_pwm = 0

        # inits buttons
        self.button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)
        pin = Pin(PWM_PIN)
        self.pwm = PWM(pin)
        self.pwm.freq(5000)


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

   
    def btn_loop(self):
        """
        Loop for check HW press button and timer.
        """
        while True:
            self.btn_check()
            utime.sleep(0.1)


if __name__ == "__main__":
    m = Main()
    m.btn_loop()
