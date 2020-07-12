# -*- coding: utf-8 -*-
#
# ***********************************************************************************
# MIT License
#
# Copyright (c) 2020 Kevin G. Schlosser
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is furnished
# to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
# CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
# OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# ***********************************************************************************

from .. import DecodeError
from .. import protocol_base


class Amcore(protocol_base.IrProtocolBase):
    frequency = 38000
    _lead_in = [8200, -4200]
    _bursts = [[600, -1500], [1500, -600]]
    _lead_out = [1900, -34300]
    bit_count = 64
    encoding = 'lsb'

    _code_order = [
        ['FAN_SPEED', 3],
        ['MODE', 3],
        ['TEMPERATURE', 6],
        ['POWER', 4],
        ['VENT', 2],
        ['TURBO', 2]
    ]

    _parameters = [
        ['FAN_SPEED', 8, 10],
        ['MODE', 13, 15],
        ['TEMPERATURE', 17, 22],
        ['POWER', 40, 43],
        ['VENT', 48, 49],
        ['TURBO', 54, 55],
        ['CHECKSUM', 56, 63]
    ]

    encode_parameters = [
        ['fan_speed', 1, 4],
        ['mode', 0, 5],
        ['temperature', 12, 32],
        ['power', 3, 12],
        ['vent', 0, 3],
        ['turbo', 0, 3]
    ]

    @property
    def power(self):
        return [3, 12]

    @property
    def vent(self):
        return [0, 3]

    @property
    def turbo(self):
        return [0, 3]

    def _compile_packet(
        self,
        fan_speed,
        mode,
        temperature,
        power,
        vent,
        turbo
    ):
        byte0 = 1
        byte1 = 0
        byte2 = 0
        byte3 = 0
        byte4 = 0
        byte5 = 0
        byte6 = 0

        byte1 = self._copy_bits(fan_speed, 0, 2, byte1, 5)
        byte1 = self._copy_bits(mode, 0, 2, byte1, 0)
        byte2 = self._copy_bits(temperature, 0, 6, byte2, 1)
        byte5 = self._copy_bits(power, 0, 3, byte5, 4)
        byte6 = self._copy_bits(vent, 0, 1, byte6, 6)
        byte6 = self._copy_bits(turbo, 0, 1, byte6, 0)

        return (
            byte0,
            byte1,
            byte2,
            byte3,
            byte4,
            byte5,
            byte6
        )

    def _calc_checksum(self, fan_speed, mode, temperature, power, vent, turbo):
        packet = self._compile_packet(
            fan_speed,
            mode,
            temperature,
            power,
            vent,
            turbo
        )

        checksum = 0
        for byte in packet:
            checksum += (byte >> 4) + (byte & 0xF)

        return self._get_bits(checksum, 0, 7)

    def decode(self, data, frequency=0):
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)

        checksum = self._calc_checksum(
            code.fan_speed,
            code.mode,
            code.temperature,
            code.power,
            code.vent,
            code.turbo
        )

        if checksum != code.checksum:
            raise DecodeError('Invalid checksum')

        return code

    def encode(self, fan_speed, mode, temperature, power, vent, turbo):
        packet = self._compile_packet(
            fan_speed,
            mode,
            temperature,
            power,
            vent,
            turbo
        )

        packet = list(packet)

        checksum = self._calc_checksum(
            fan_speed,
            mode,
            temperature,
            power,
            vent,
            turbo
        )

        packet += [checksum]

        for i, item in enumerate(packet):
            packet[i] = list(self._get_timing(item, j) for j in range(8))

        packet = self._build_packet(*packet)

        params = dict(
            frequency=self.frequency,
            FAN=fan_speed,
            MODE=mode,
            TEMPERATURE=temperature,
            POWER=power,
            VENT=vent,
            TURBO=turbo
        )

        code = protocol_base.IRCode(
            self,
            [packet[:]],
            [packet[:]],
            params
        )
        return code


Amcore = Amcore()
