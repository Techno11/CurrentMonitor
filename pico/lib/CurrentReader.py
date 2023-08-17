from machine import I2C, Pin
from time import ticks_ms
from lib.external.ADS1115 import ADS1115
from lib.Mux16 import Mux16
from constants.constants import get_debug, CT_MULTIPLIER

d_print = get_debug("ADS")

# Attempt to define an ADS
def __get_ads(address, i2c):
    try:
        ads = ADS1115(i2c, address, 4)
        ads.read(channel1=0, channel2=1)
        return ads
    except:
        d_print(f"ADS addressed with {str(address)} unavaliable")
        return None

class CurrentReader:
    def __init__(self):
        # Configure I2C
        i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=400000)

        # Check for and enable ADS addressed on Ground
        d_print("Checking for ADS addressed with 0x48 (ADDR -> GND)")
        self.ads_0 = __get_ads(0x48, i2c)

        # Check for and enable ADS addressed on VCC
        d_print("Checking for ADS addressed with 0x49 (ADDR -> VCC)")
        self.ads_1 = __get_ads(0x49, i2c)

        # Check for and enable ADS addressed on SDA
        d_print("Checking for ADS addressed with 0x4A (ADDR -> SDA)")
        self.ads_2 = __get_ads(0x4A, i2c)

        # Check for and enable ADS addressed on SCL
        d_print("Checking for ADS addressed with 0x4B (ADDR -> SCL)")
        self.ads_3 = __get_ads(0x4B, i2c)

        # Configure Mux
        self.mux = Mux16(18, 19, 20, 21)

    # Return which ADSs are active
    def get_active(self):
        final = []
        # If we have ADS 0
        if self.ads_0 is not None: final.append(0)
        
        # If we have ADS 1
        if self.ads_1 is not None: final.append(1)
        
        # If we have ADS 2
        if self.ads_2 is not None: final.append(2)
        
        # If we have ADS 3
        if self.ads_3 is not None: final.append(3)

        return final

    def read_next(self):
        # Next Mux
        self.mux.next()

        # Record Start time
        start_time = ticks_ms()

        # Accumulators and counter
        max_0 = 0
        max_1 = 0
        max_2 = 0
        max_3 = 0
        counter = 0

        # Loop until returned
        while(True):
            if ticks_ms() - start_time <= 1000:
                # Check ADS #1
                if self.ads_0 is not None:
                    raw = self.ads_0.read(channel1=0, channel2=1)
                    max_0 = max(abs(raw), max_0)

                # Check ADS #2
                if self.ads_1 is not None:
                    raw = self.ads_1.read(channel1=0, channel2=1)
                    max_1 = max(abs(raw), max_1)

                # Check ADS #3
                if self.ads_2 is not None:
                    raw = self.ads_2.read(channel1=0, channel2=1)
                    max_2 = max(abs(raw), max_2)

                # Check ADS #4
                if self.ads_3 is not None:
                    raw = self.ads_3.read(channel1=0, channel2=1)
                    max_3 = max(abs(raw), max_3)
                
                counter += 1
            else: 
                final = []
                pin = self.mux.get_active();
                
                # If we have ADS 0, calc and append
                if self.ads_0 is not None: final.append({"device": 0, "pin": pin, "current": max_0 * CT_MULTIPLIER})
                
                # If we have ADS 1, calc and append
                if self.ads_1 is not None: final.append({"device": 1, "pin": pin, "current": max_1 * CT_MULTIPLIER})
                
                # If we have ADS 2, calc and append
                if self.ads_2 is not None: final.append({"device": 2, "pin": pin, "current": max_2 * CT_MULTIPLIER})
                
                # If we have ADS 3, calc and append
                if self.ads_3 is not None: final.append({"device": 3, "pin": pin, "current": max_3 * CT_MULTIPLIER})

                return final