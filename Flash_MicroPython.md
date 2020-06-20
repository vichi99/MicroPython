 # Prepare Nodemcu(ESP8226) for MicroPython
 ![nodemcu](images/nodemcu_pinout.jpg)
 
 ## Control Device
 
 - run this command for check actual tty state. 
 ``` 
 ls /dev/tty.* 
 ```
 
 - Now connect device to USB, rerun the command and check changes in output. We should see like `/dev/tty.SLAB_USBtoUART` or something similar. If not go to [this page](https://www.silabs.com/products/development-tools/software/usb-to-uart-bridge-vcp-drivers) and download CP210x USB driver.
 ```
 IMPORTANT! Use only data usb cabel. I and a lot of people on this world spend many many... 
 time connecting device with wrong cable only for powering.
 ```
 
 ## Dependencies
 
 - Download MicroPython for our Nodemcu(esp8266) module. You can download it from [this page](http://micropython.org/download#esp8266). My latest choice was `esp8266-20191220-v1.12.bin`.
 
 - For deploying we will use [esptool](https://github.com/espressif/esptool/) which can install it using pip:
 ```
 pip install esptool
 ```
 
 ## Deploy
 
 1. Erase flash.
 ```
 esptool.py --port /dev/tty.SLAB_USBtoUART erase_flash
 ```
 2. Deploy flash.
 ```
 esptool.py --port /dev/tty.SLAB_USBtoUART --baud 115200 write_flash --flash_size=detect 0 esp8266-20191220-v1.12.bin
 ```
 
 ### Original source
 - For created this manual was used this page [https://docs.micropython.org/en/latest/esp8266/tutorial/intro.html](https://docs.micropython.org/en/latest/esp8266/tutorial/intro.html)
 - I was inspirated by this page too.[https://naucse.python.cz/](https://naucse.python.cz/)
 
 
