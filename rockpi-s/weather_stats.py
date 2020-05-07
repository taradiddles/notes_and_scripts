#!/usr/bin/python3

import adafruit_dps310
from adafruit_extended_bus import ExtendedI2C as I2C
from adafruit_dps310 import *

i2c = I2C(0)

class iDPS310(DPS310):

    _reg0e = RWBits(8, 0x0E, 0)
    _reg0f = RWBits(8, 0x0F, 0)
    _reg62 = RWBits(8, 0x62, 0)

    def _correct_temp(self):
        self._reg0e = 0xA5
        self._reg0f = 0x96
        self._reg62 = 0x02
        self._reg0e = 0
        self._reg0f = 0
        unused_var = self._raw_temperature

    def _reset(self):
        # print('override reset')
        self._reset_register = 0x89
        # wait for hardware reset to finish
        sleep(0.010)
        while not self._sensor_ready:
            sleep(0.001)
        self._correct_temp()

#dps310 = adafruit_dps310.DPS310(i2c) 
dps310 = iDPS310(i2c)
sleep(1)
print('temp:{:.2f} pressure:{:.2f}'.format(dps310.temperature,dps310.pressure))


