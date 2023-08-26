# https://github.com/flrrth/pico-bh1750

import math

from micropython import const
from utime import sleep_ms


class BH1750Simple:

    MEASUREMENT_TIME = const(120)

    def __init__(self, i2c, addr=0x23, debug=False, period=150):
        self.i2c = i2c
        self.period = period
        self.addr = addr
        self.time = 0
        self.value = 0
        self.i2c.writeto(addr, bytes([0x10])) # start continuos 1 Lux readings every 120ms

    def read(self):
        self.time += self.period
        if self.time >= self.MEASUREMENT_TIME:
            self.time = 0
            data = self.i2c.readfrom(self.addr, 2)
            self.value = (((data[0] << 8) + data[1]) * 1200) // 1000
        return self.value
