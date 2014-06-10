import time

from Adafruit_I2C import Adafruit_I2C

from util import timestamp_to_base64

class TSL2561:
    ADDR_FLOAT = 0x39 # Default address (pin left floating)

    COMMAND_BIT = 0x80 # Must be 1
    WORD_BIT    = 0x20 # 1 = read/write word (rather than byte)

    CONTROL_POWERON  = 0x03
    CONTROL_POWEROFF = 0x00

    REGISTER_CONTROL          = 0x00
    REGISTER_TIMING           = 0x01
    REGISTER_CHAN0_LOW        = 0x0C
    REGISTER_CHAN1_LOW        = 0x0E

    INTEGRATIONTIME_13MS      = 0x00 # 13.7ms
    GAIN_1X                   = 0x00 # No gain

def poweron(i2c):
    i2c.write8(TSL2561.COMMAND_BIT|TSL2561.REGISTER_CONTROL, TSL2561.CONTROL_POWERON)

def poweroff(i2c):
    i2c.write8(TSL2561.COMMAND_BIT|TSL2561.REGISTER_CONTROL, TSL2561.CONTROL_POWEROFF)

def check_state(i2c):
    # this should check the photo sensor and return True if it senses that the
    # LED is on, otherwise return False.

    poweron(i2c)
    time.sleep(0.014)
    broadband = i2c.reverseByteOrder(i2c.readU16(TSL2561.COMMAND_BIT|TSL2561.WORD_BIT|TSL2561.REGISTER_CHAN0_LOW))
    ir = i2c.reverseByteOrder(i2c.readU16(TSL2561.COMMAND_BIT|TSL2561.WORD_BIT|TSL2561.REGISTER_CHAN1_LOW))
    poweroff(i2c)

    background = max(0, broadband - ir)
    isolated_ir = ir - background*2
    blink = isolated_ir >= 10

    return time.time(), blink

def run():
    i2c = Adafruit_I2C(TSL2561.ADDR_FLOAT)
    poweron(i2c)
    i2c.write8(TSL2561.COMMAND_BIT|TSL2561.REGISTER_TIMING, TSL2561.GAIN_1X|TSL2561.INTEGRATIONTIME_13MS)
    poweroff(i2c)

    f = open("blink-log", "a")
    last_state = False
    while True:
        ts, state = check_state(i2c)
        if state == True and last_state == False: # mark the beginning of the blink
            f.write(timestamp_to_base64(ts) + "\n") # deciseconds
            f.flush()

        last_state = state

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        pass
