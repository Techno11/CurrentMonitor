from ubinascii import hexlify
import network
from constants.secrets import PASSWORD, SSID, STATIC
from time import sleep
from constants.constants import get_debug

status_map = {
    01: "Connecting",
    -1: "Connection Failed",
    03: "Got IP (Connection Successful)",
    00: "Idle",
    -2: "No Access Point Found",
    -3: "Wrong Password"
}

d_print = get_debug("Wifi")

class PicoWifi:
    
    def __init__(self):
        # Debug
        d_print("Initilizing Wifi Module")

        # Setup Wifi Mode
        self.wlan = network.WLAN(network.STA_IF)

        # Set Wifi as Active
        self.wlan.active(True)

    def connect(self):
        # Command HW to connect
        self.__hw_connect()

        # Sleep 1 second to allow startup connection
        sleep(1)

        # Wait for connection
        while not self.is_connected():
            status = self.status()
            if status < 0:
                d_print(f"Failed to connect. {self.status_friendly()}. Retrying...")
                self.disconnect()
                self.__hw_connect()
            elif status == 0:
                # Wifi doing nothing, try connecting
                self.__hw_connect()
            else:
                # Wifi is connecting, sleep for 1 second and check again
                d_print(f"Wifi Connecting: {self.status_friendly()}")
                sleep(1)
        d_print(f"Connected to {SSID}")

    # Ensure that we're connected to Wifi
    def ensure_connected(self):
        if not self.is_connected:
            self.connect()
            
    def __hw_connect(self):
        # Debug
        d_print(f"Attempting to connect to {SSID}")
        # Set Static IP
        if STATIC is not None:
            self.wlan.ifconfig((STATIC["ip"], STATIC["subnet"], STATIC["gateway"], STATIC["DNS"]))

        self.wlan.connect(SSID, PASSWORD)

    def disconnect(self):
        d_print("Disconnecting")
        self.wlan.disconnect()

    def is_connected(self):
        return self.wlan.isconnected()

    def status_friendly(self):
        return status_map[self.wlan.status()]

    def get_mac(self):
        wlan_mac = self.wlan.config('mac')
        return hexlify(wlan_mac).decode()

    def status(self):
        # -3 – failed due to incorrect password,
        # -2 – failed because no access point replied,
        # -1 – failed due to other problems,
        # 0 – no connection and no activity,
        # 1 – connecting in progress,
        # 3 – connection successful.
        return self.wlan.status()
