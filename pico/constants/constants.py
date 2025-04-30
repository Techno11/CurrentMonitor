
# Enable Debugging
DEBUG = False

# Software Version
VERSION = "0.0.1"

# Current Transformer Configurations
CT_MULTIPLIER = 0.009
CT_OFFSET = .04 # Rough amp offset noted @ 0 amps

# Power configuration
AC_VOLTS = 123

# Calibration datapoints.  Every sensor is different.... so this is really bad practice.
# These must be floats, and point 1 the 0 amp measurement, and point 2 higher than that
CALIBRATION_DATA_1 = [0.0, 2.70] # 0A = 0.123V 
CALIBRATION_DATA_2 = [5.29, 75.67254] # 4A = 0.234V

# If this is set to true, it will use the calibration data to calculate the current. Otherwise, it will generically apply the CT_MULTIPLIER
USE_CALIBRATION = False

# Get a debug lambda function to call from each module
def get_debug(module):
    return lambda p: print(f"{module} | {p}") if DEBUG else None