from machine import Pin
from constants.constants import get_debug


def get_bin(x):
    """
    Get the binary representation of x.

    Parameters
    ----------
    x : int

    Returns
    -------
    string
    """
    # Convert to binary
    b = "{0:b}".format(x)
    # Hack to get around un-implimented methods like zfill
    while len(b) < 4:
        b = "0" + b
    return b

d_print = get_debug("Mux16")

class Mux16:
    current = 0

    def __init__(self, pin_0, pin_1, pin_2, pin_3):
        # Debug
        d_print("Initilizing Muxer")

        # Define Pins
        self.s0 = Pin(pin_0, Pin.OUT)
        self.s1 = Pin(pin_1, Pin.OUT)
        self.s2 = Pin(pin_2, Pin.OUT)
        self.s3 = Pin(pin_3, Pin.OUT)

        # Set all low
        self.s0.value(0)
        self.s1.value(0)
        self.s2.value(0)
        self.s3.value(0)

    # Return active input
    def get_active(self):
        return self.current

    # Call up an input
    def mux(self, input):
        if input > 15: 
            self.current = 0
        else:
            self.current = input
        d_print(f"Calling up {self.current}")
        input_binary = get_bin(self.current)
        self.s0.value(int(input_binary[3]))
        self.s1.value(int(input_binary[2]))
        self.s2.value(int(input_binary[1]))
        self.s3.value(int(input_binary[0]))

    def next(self):
        self.mux(self.current + 1)

    