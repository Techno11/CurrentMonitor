
# Enable Debugging
DEBUG = True

# Software Version
VERSION = "0.0.1"

# Current Transformer Configurations
CT_MULTIPLIER = 0.009

# Power configuration
AC_VOLTS = 123

# Get a debug lambda function to call from each module
def get_debug(module):
    return lambda p: print(f"{module} | {p}") if DEBUG else None