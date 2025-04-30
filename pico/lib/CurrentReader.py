import math
from machine import I2C, Pin
from time import ticks_ms
from lib.external.ADS1115 import ADS1115
from lib.Mux16 import Mux16
from constants.constants import CALIBRATION_DATA_1, CALIBRATION_DATA_2, CT_OFFSET, USE_CALIBRATION, get_debug, CT_MULTIPLIER

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
    
    
# Calculate RMS
def calculate_rms(data):
    if not data:
        return 0
    squared_sum = sum(x * x for x in data)
    return (math.sqrt(squared_sum / len(data)))

def linear_filter(raw_voltage):
    if USE_CALIBRATION:
        amperage_pt1, voltage_pt1 = CALIBRATION_DATA_1
        amperage_pt2, voltage_pt2 = CALIBRATION_DATA_2 

        # Calculate the slope (gain) of the linear relationship (Amps per Volt).
        slope = (amperage_pt2 - amperage_pt1) / (voltage_pt2 - voltage_pt1)

        # Calculate the y-intercept (offset) of the linear relationship (Amps).
        offset = -slope * voltage_pt1

        # Apply the linear transformation to get the calibrated current.
        calibrated_current = (slope * raw_voltage) + offset

        return calibrated_current
    else:
        # Apply the generic multiplier
        amps = (raw_voltage * CT_MULTIPLIER) - CT_OFFSET
        
        if amps < 0:
            amps = 0
            
        return amps

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

        # Lists to store raw readings for each ADS
        readings_0 = []
        readings_1 = []
        readings_2 = []
        readings_3 = []

        # Loop until returned
        while ticks_ms() - start_time <= 500:
            if self.ads_0 is not None:
                readings_0.append(self.ads_0.read(channel1=0, channel2=1))
            if self.ads_1 is not None:
                readings_1.append(self.ads_1.read(channel1=0, channel2=1))
            if self.ads_2 is not None:
                readings_2.append(self.ads_2.read(channel1=0, channel2=1))
            if self.ads_3 is not None:
                readings_3.append(self.ads_3.read(channel1=0, channel2=1))
                
        final = []
        pin = self.mux.get_active()
        
        # If we have ADS 0, calc and append
        if self.ads_0 is not None and readings_0:
            rms_0 = calculate_rms(readings_0)
            final.append({"device": 0, "pin": pin, "current": linear_filter(rms_0)})
            
        # If we have ADS 1, calc and append
        if self.ads_1 is not None and readings_1:
            rms_1 = calculate_rms(readings_1)
            final.append({"device": 1, "pin": pin, "current": linear_filter(rms_1)})
            
        # If we have ADS 2, calc and append
        if self.ads_2 is not None and readings_2:
            rms_2 = calculate_rms(readings_2)
            final.append({"device": 2, "pin": pin, "current": linear_filter(rms_2)})
            
        # If we have ADS 3, calc and append
        if self.ads_3 is not None and readings_3:
            rms_3 = calculate_rms(readings_3)
            final.append({"device": 3, "pin": pin, "current": linear_filter(rms_3)})

        return final