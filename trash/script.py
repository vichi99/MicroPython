from machine import Pin, PWM
from neopixel import NeoPixel
from time import sleep

#################
# screen /dev/tty.SLAB_USBtoUART 115200
#
#
# brew install picocom
# picocom -b 115200 --flow n /dev/tty
#################

# pin_btn = Pin(0, Pin.IN)
# pin_led = Pin(14, Pin.OUT)

# while True:
#     pin_led.value(1)
#     sleep(1/2)
#     pin_led.value(0)
#     sleep(1/2)

# 1024 full duty
# duty = 1024
# while True:
#     pwm = PWM(pin_led, freq=10, duty=duty)
#         pwm.freq(4)

# pin_buzzer = Pin(13, Pin.OUT)
# while True:
#     pwm_buzzer = PWM(pin_buzzer, freq=440, duty=14)

# pin_servo = Pin(2, Pin.OUT)
# # while True:
# pwm_servo = PWM(pin_servo, freq=50, duty=77)
# pwm_servo.duty(40) # 0 stupnu
# # pwm_servo.duty(180)
# sleep(1)
# pwm_servo.duty(180) # 180
# # pwm_servo.duty(155) # 180



NUM_LEDS = 8
pin = Pin(12, Pin.OUT)
np = NeoPixel(pin, NUM_LEDS)
num = 1
while True:
    np[0] = (num, 25, 255)
    np[1] = (0, num, 100)
    np[2] = (2, 25, 255)
    np[3] = (25, 25, num)
    np.write()
    sleep(0.5)
    num += 20
    if num >= 256:
        num = 1