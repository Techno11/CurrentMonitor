from constants.constants import get_debug
from lib.HealthManager import HealthManager
from lib.Heartbeat import Heartbeat
from lib.CurrentReader import CurrentReader
from lib.Wifi import PicoWifi
from lib.MQTT import PicoMQTTClient
from time import sleep, time
import machine

# Heartbeat flashes the onboard LED to signal that we're alive and we'ven't crashed, also feeds watchdog
hb = Heartbeat()

# Works with the Analog Muxer to read the current from our 16 inputs
reader = CurrentReader()

# Setup Wifi
wifi = PicoWifi()
wifi.connect()

# Setup MQTT
mqtt = PicoMQTTClient(wifi.get_mac())
mqtt.connect()

# Get Logging instance
d_print = get_debug("Main")

# Startup Time 
startTime = time()  

# Send out discover payloads to MQTT broker, 16 per ADS that we're connected to
for x in reader.get_active(): mqtt.discover(x)

# Publish Ready
health_manager = HealthManager(mqtt)
health_manager.is_healthy()

# Main loop
while(True):
    # If uptime is greater than 24 hour, restart
    if (time() - startTime) > 86400:
        machine.reset()

    # Do Heartbeat, feed watchdog
    hb.hb()
    
    try:
        # Ensure we're connected
        wifi.ensure_connected()

        # Read and publish current
        readings = reader.read_next()
        for reading in readings:
            mqtt.publish_current(reading["device"], reading["pin"], reading["current"])
        
        # Send healthy message if we've recovered, and we've made it here
        health_manager.is_healthy()
    except Exception as e:
        # Send unhealthy message
        health_manager.is_unhealthy(str(e))

        # Restart
        machine.reset()



