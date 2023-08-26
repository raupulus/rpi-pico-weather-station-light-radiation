#!/usr/bin/python3
# -*- encoding: utf-8 -*-

# @author     Raúl Caro Pastorino
# @email      dev@fryntiz.es
# @web        https://fryntiz.es
# @gitlab     https://gitlab.com/fryntiz
# @github     https://github.com/fryntiz
# @twitter    https://twitter.com/fryntiz
# @telegram   https://t.me/fryntiz

# Create Date: 2019/10/27
# Project Name:
# Description:
#
# Dependencies:
#
# Revision 0.01 - File Created
# Additional Comments:

# @copyright  Copyright © 2019 Raúl Caro Pastorino
# @license    https://wwww.gnu.org/licenses/gpl.txt

# Copyright (C) 2019  Raúl Caro Pastorino
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

# Guía de estilos aplicada: PEP8

# #           Descripción           # #
# Clase para obtener datos y modelo de datos para DB con el sensor veml6070
# Sensor rayos UV
# Esta clase puede funcionar de forma autónoma, aún así también es extendida
# por clases hijas para seccionar el tipo de resultado obtenido y tratarse de
# forma independiente en aplicaciones que lo implementen.

import time
from ustruct import unpack

_VEML6075_ADDR = 0x10

_REG_CONF    = 0x00
_REG_UVA     = 0x07
_REG_DARK    = 0x08  # check is true?
_REG_UVB     = 0x09
_REG_UVCOMP1 = 0x0A
_REG_UVCOMP2 = 0x0B
_REV_ID      = 0x0C


# Valid constants for UV Integration Time
_VEML6075_UV_IT = { 50: 0x00, 100: 0x01, 200: 0x02, 400: 0x03, 800: 0x04 }

class VEML6075:
    def __init__(
            self,
            i2c,
            debug=False,
            integration_time=100,
            high_dynamic= True,
            uva_a_coef= 2.22,
            uva_b_coef= 1.33,
            uvb_c_coef= 2.95,
            uvb_d_coef= 1.74,
            uva_response= 0.001461,
            uvb_response= 0.002591 ):

        print('VEML6075 Update: ', 3)

        self.i2c = i2c

        # Set coefficients
        self._addr = _VEML6075_ADDR
        self._a = uva_a_coef
        self._b = uva_b_coef
        self._c = uvb_c_coef
        self._d = uvb_d_coef
        self._uvaresp = uva_response
        self._uvbresp = uvb_response
        self._uvacalc = self._uvbcalc = None
        # Init I2C
        self._i2c = i2c
        # read ID!
        veml_id = self._read_register(_REV_ID)
        if veml_id != 0x26:
            raise RuntimeError("Incorrect VEML6075 ID 0x%02X" % veml_id)
        # shut down
        self._write_register(_REG_CONF, 0x01)
        # Set integration time
        self.integration_time = integration_time
        # enable
        conf = self._read_register(_REG_CONF)
        if high_dynamic:
            conf |= 0x08
        conf &= ~0x01  # Power on
        self._write_register(_REG_CONF, conf)

    def _take_reading(self):
        """Perform a full reading and calculation of all UV calibrated values"""
        time.sleep(0.1)
        uva = self._read_register(_REG_UVA)
        uvb = self._read_register(_REG_UVB)
        #dark = self._read_register(_REG_DARK)
        uvcomp1 = self._read_register(_REG_UVCOMP1)
        uvcomp2 = self._read_register(_REG_UVCOMP2)
        # Equasion 1 & 2 in App note, without 'golden sample' calibration
        self._uvacalc = uva - (self._a * uvcomp1) - (self._b * uvcomp2)
        self._uvbcalc = uvb - (self._c * uvcomp1) - (self._d * uvcomp2)
        #print("UVA = %d, UVB = %d, UVcomp1 = %d, UVcomp2 = %d, Dark = %d" %
        #      (uva, uvb, uvcomp1, uvcomp2, dark))

    @property
    def uva(self):
        """The calibrated UVA reading, in 'counts' over the sample period"""
        self._take_reading()
        return self._uvacalc

    @property
    def uvb(self):
        """The calibrated UVB reading, in 'counts' over the sample period"""
        self._take_reading()
        return self._uvbcalc

    @property
    def uv_index(self):
        """The calculated UV Index"""
        self._take_reading()
        return ((self._uvacalc * self._uvaresp) + (self._uvbcalc * self._uvbresp)) / 2

    @property
    def integration_time(self):
        """The amount of time the VEML is sampling data for, in millis.
        Valid times are 50, 100, 200, 400 or 800ms"""
        key = (self._read_register(_REG_CONF) >> 4) & 0x7
        for k, val in enumerate(_VEML6075_UV_IT):
            if key == k:
                return val
        raise RuntimeError("Invalid integration time")

    @integration_time.setter
    def integration_time(self, val):
        if not val in _VEML6075_UV_IT.keys():
            raise RuntimeError("Invalid integration time")
        conf = self._read_register(_REG_CONF)
        conf &= ~ 0b01110000 # mask off bits 4:6
        conf |= _VEML6075_UV_IT[val] << 4
        self._write_register(_REG_CONF, conf)

    def _read_register(self, register):
        """Read a 16-bit value from the `register` location"""
        result = unpack('BB', self._i2c.readfrom_mem(self._addr, register, 2))
        return ( (result[1] << 8) | result[0] )

    def _write_register(self, register, value):
        """Write a 16-bit value to the `register` location"""
        self._i2c.writeto_mem(self._addr, register, bytes([value, value >> 8]))
