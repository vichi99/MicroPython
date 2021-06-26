###############################################
#
# Script for control led strips
# through button and html template.
#
################################################
#
# Jan Vicha
# 2021
# VER = 26-6-2021
#
################################################

import time
import uasyncio
import uselect as select
from machine import Pin

##### SETTINGS
button = Pin(15, Pin.IN, Pin.PULL_UP)

pin = machine.Pin(14)
pwm=machine.PWM(pin)
pwm.freq(5000)

DUTY_LEVELS=[0,1,5,50,100]
MAX_DUTY=1023
ACTUAL_PERC_PWM= 0
DELAY_BTN_PRESS = 1000
LED_OFF_HOUR = "23"
LED_OFF_MINUTE = "00"
##############

def timer_check():
  """
  Check if is time to turn off led.
  """
  local_time = time.localtime()
  hour = int(local_time[3])
  minute = int(local_time[4])
  sec = int(local_time[5])
  if int(LED_OFF_HOUR) == hour and int(LED_OFF_MINUTE) == minute and sec == 0:
    turn_off_led()

def btn_check():
  t1 = time.ticks_ms()
  end = False
  if button.value() == 1:
    time.sleep(0.1)
    # for long btn press turn off
    while button.value() == 1:
      if time.ticks_ms() - t1 > DELAY_BTN_PRESS:
          turn_off_led()
          time.sleep(1)
          end = True
          break
    if not end and button.value() == 0:
        btn_press()
        time.sleep(0.1)

def btn_press():
  for index, level in enumerate(DUTY_LEVELS):
    if ACTUAL_PERC_PWM == level:
      # If last item
      if index + 1 == len(DUTY_LEVELS):
        turn_off_led()
      else:
        set_perc_pwm(DUTY_LEVELS[index + 1])
      break

def set_perc_pwm(value_percent):
  global ACTUAL_PERC_PWM
  ACTUAL_PERC_PWM = value_percent
  pwm.duty(int(MAX_DUTY * value_percent / 100))

def turn_off_led():
  set_perc_pwm(DUTY_LEVELS[0])

def web_page():
  
  html = """<html><head>
  <title>LED</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="data:,"> <style>html{font-family: Helvetica; display:inline-block; margin: 0px auto; text-align: center; 
  background-color: gray};
  h1{color: #0F3376; padding: 2vh;}p{font-size: 1.5rem;}.button{display: inline-block; background-color: #e7bd3b; border: none; 
  border-radius: 4px; color: white; padding: 12px 32px; text-decoration: none; font-size: 24px; margin: 2px; cursor: pointer;}
  .button2{background-color: #4286f4;}

  label {
    display: block;
    font: 1rem 'Fira Sans', sans-serif;
  }

  input,
  label {
      margin: .4rem 0;
  }
  </style></head>
  
  <body>
  
  <h1>Led zapnuto na: <strong>"""+str(ACTUAL_PERC_PWM)+"""%</strong></h1>
  
  <p><a href="/?led=0"><button class="button">0%</button></a></p>
  <p><a href="/?led=1"><button class="button button2">1%</button></a></p>
  <p><a href="/?led=5"><button class="button button2">5%</button></a></p>
  <p><a href="/?led=50"><button class="button button2">50%</button></a></p>
  <p><a href="/?led=100"><button class="button button2">100%</button></a></p>
  <form>

  <p>Casovac vypnuti na: <strong>"""+LED_OFF_HOUR+""":"""+LED_OFF_MINUTE+"""</strong></p>
  <input type="time" id="from" name="from"
    required>
  <input type="submit" value="Nastavit">

</form>

  </body></html>"""
  return html

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

def web_app_loop():
  global LED_OFF_HOUR, LED_OFF_MINUTE
  while True:
    # select for sync control input from web and btn press
    r, w, err = select.select((s,), (), (), 0.1)
    if r:
      for readable in r:
        try:
          conn, addr = s.accept()
          print('Got a connection from %s' % str(addr))
          request = conn.recv(1024)
          if not request:
            continue
          request = str(request)
          led_txt = request.split()[1]

          led_from = request.find('/?from=')
          if led_txt == '/?led=0':
            set_perc_pwm(0)
          elif led_txt == '/?led=1':
            set_perc_pwm(1)
          elif led_txt == '/?led=5':
            set_perc_pwm(5)
          elif led_txt == '/?led=50':
            set_perc_pwm(50)
          elif led_txt == '/?led=100':
            set_perc_pwm(100)
          elif led_from == 6:
            LED_OFF_HOUR = led_txt[led_txt.find("from")+5:].split("%3A")[0]
            LED_OFF_MINUTE = led_txt[led_txt.find("from")+5:].split("%3A")[1]

          response = web_page()
          conn.send('HTTP/1.1 200 OK\n')
          conn.send('Content-Type: text/html\n')
          conn.send('Connection: close\n\n')
          conn.sendall(response)
          conn.close()
        except OSError as e:
          pass
    btn_check()
    timer_check()


def m():
  web_app_loop()

m()