try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")
import time

GPIO.setmode(GPIO.BOARD)

channel = 16

GPIO.setup(channel, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def my_callback(channel):
    print('This is a edge event callback function!')
    print('Edge detected on channel %s'%channel)
    print('This is run in a different thread to your main program')

GPIO.add_event_detect(channel, GPIO.RISING, callback=my_callback, bouncetime=500) 

while True:
	time.sleep(0.01)  # wait 10 ms to give CPU chance to do other things

print "Pressed"
