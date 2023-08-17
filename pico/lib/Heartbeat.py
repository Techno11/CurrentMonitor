from machine import Pin, WDT

# Watchdog
watchdog = WDT(timeout=8388)

class Heartbeat:
    def __init__(self):
        # LED Pin
        self.led_pin = Pin("LED", Pin.OUT)
        

    def hb(self):
        self.led_pin.toggle()
        watchdog.feed()
