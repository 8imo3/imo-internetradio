import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)

print("Várakozás gombnyomásra...")

try:
    while True:
        if GPIO.input(17) == 0:
            print("Gomb LENYOMVA!")
            time.sleep(0.5)
except KeyboardInterrupt:
    GPIO.cleanup()
