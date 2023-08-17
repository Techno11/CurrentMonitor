from constants.constants import get_debug
from lib.MQTT import PicoMQTTClient
from time import ticks_ms, sleep_ms
from machine import reset


d_print = get_debug("HealthManager")

class HealthManager:

    healthy = False
    last_log = ""
    err_start = -1

    def __init__(self, mqtt: PicoMQTTClient):
        d_print("Initilizing")
        self.mqtt = mqtt

    def is_healthy(self):
        if self.healthy is not True:
            self.healthy = True
            self.last_log = ""
            d_print("Healthy")
            try:
                self.mqtt.publish_log("Healthy")
            except:
                d_print("Failed to publish log")

    def is_unhealthy(self, log):
        # Error Start date on first error
        if self.healthy:
            self.err_start = ticks_ms()

        # If we're unhealthy or the log has changed
        if self.healthy or self.last_log != log:
            self.healthy = False
            self.last_log = log
            d_print(f"Unhealthy: {log}")
            try:
                self.mqtt.publish_log(log)
            except: 
                d_print("Failed to publish log")

        # Restart after 10 seconds of failure
        if not self.healthy and self.err_start > -1 and ticks_ms() - self.err_start > 10000:
            # Attempt to publish last log
            try:
                self.mqtt.publish_log(f"Restarting due to prolonged error: {self.last_log}")
            except:
                d_print("Unable to publish last log. Restarting...")
            # Sleep for 1 second
            sleep_ms(1000)
            # Reset
            reset()
