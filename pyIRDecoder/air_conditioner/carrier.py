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


'''
  F    6     2      9     A     C    C      D
1111  0110  0010  1001  1010  1100  1100  1101
'''


class Carrier(protocol_base.IrProtocolBase):
    frequency = 38000

    _lead_in = [8532, -4228]
    _bursts = [[628, -532], [628, -1320]]
    _lead_out = [628, -20000]
    bit_count = 32
    encoding = 'msb'

    _code_order = [
        ['MODE', 3],
        ['TEMPERATURE', 5],
        ['FAN_SPEED', 2],
        ['ROOM_TEMPERATURE', 5],
        ['SLEEP', 1],
        ['TURBO', 1],
        ['POWER', 1],
        ['FEEL', 1]
    ]

    _parameters = [
        ['CHECKSUM1', 0, 7],
        ['CHECKSUM2', 8, 15],
        ['MODE', 19, 21],
        ['TEMPERATURE', 22, 26],
        ['FAN_SPEED', 27, 28],
        ['ROOM_TEMPERATURE', 29, 33],
        ['SLEEP', 74, 74],
        ['TURBO', 75, 75],
        ['POWER', 77, 77],
        ['FEEL', 79, 79],
        ['CHECKSUM3', 80, 87],
        ['CHECKSUM4', 88, 95]
    ]

    encode_parameters = [
        ['mode', 0, 6],
        ['temperature', 10, 32],
        ['fan_speed', 0, 3],
        ['room_temperature', 10, 35],
        ['sleep', 0, 1],
        ['turbo', 0, 1],
        ['power', 0, 1],
        ['feel', 0, 1]
    ]

    def _compile_packet(
        self,
        mode,
        temperature,
        fan_speed,
        room_temperature,
        sleep,
        turbo,
        power,
        feel
    ):
        byte0 = 0b10101100
        byte1 = 0b11110101
        byte2 = 0
        byte3 = 0
        byte4 = 0
        byte5 = 0
        byte6 = 0
        byte7 = 0
        byte8 = 0
        byte9 = 0

        byte2 = self._copy_bits(mode, 0, 2, byte2, 3)
        byte2 = self._copy_bits(temperature, 0, 2, byte2, 6)
        byte3 = self._copy_bits(temperature, 3, 5, byte3, -3)
        byte3 = self._copy_bits(fan_speed, 0, 1, byte3, 3)
        byte3 = self._copy_bits(room_temperature, 0, 2, byte3, 5)
        byte4 = self._copy_bits(room_temperature, 3, 4, byte4, -3)

        byte9 = self._copy_bits(sleep, 0, 0, byte9, 2)
        byte9 = self._copy_bits(turbo, 0, 0, byte9, 3)
        byte9 = self._copy_bits(power, 0, 0, byte9, 5)
        byte9 = self._copy_bits(feel, 0, 0, byte9, 7)
        byte10 = 0b00000010

        return (
            byte0,
            byte1,
            byte2,
            byte3,
            byte4,
            byte5,
            byte6,
            byte7,
            byte8,
            byte9,
            byte10
        )

    def _calc_checksum(
        self,
        mode,
        temperature,
        fan_speed,
        room_temperature,
        sleep,
        turbo,
        power,
        feel
    ):
        packet = self._compile_packet(
            mode,
            temperature,
            fan_speed,
            room_temperature,
            sleep,
            turbo,
            power,
            feel
        )

        checksum = 2
        for byte in packet[:-1]:
            checksum += byte

        return self._get_bits(checksum, 0, 7)

    def decode(self, data, frequency=0):
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)

        if (
            code.checksum1 != 0b10101100 or
            code.checksum2 != 0b11110101 or
            code.checksum3 != 0b00000010
        ):
            raise DecodeError('Invalid checksum')

        checksum4 = self._calc_checksum(
            code.mode,
            code.temperature,
            code.fan_speed,
            code.room_temperature,
            code.sleep,
            code.turbo,
            code.power,
            code.feel
        )

        if code.checksum4 != checksum4:
            raise DecodeError('Invalid checksum')

        return code

    def encode(
        self,
        mode,
        temperature,
        fan_speed,
        room_temperature,
        sleep,
        turbo,
        power,
        feel
    ):

        packet = self._compile_packet(
            mode,
            temperature,
            fan_speed,
            room_temperature,
            sleep,
            turbo,
            power,
            feel
        )
        packet = list(packet)

        checksum = self._calc_checksum(
            mode,
            temperature,
            fan_speed,
            room_temperature,
            sleep,
            turbo,
            power,
            feel
        )

        packet += [checksum]

        for i, item in enumerate(packet):
            packet[i] = list(self._get_timing(item, j) for j in range(8))

        packet = self._build_packet(*packet)

        params = dict(
            frequency=self.frequency,
            MODE=mode,
            TEMPERATURE=temperature,
            FAN_SPEED=fan_speed,
            ROOM_TEMPERATURE=room_temperature,
            SLEEP=sleep,
            TURBO=turbo,
            POWER=power,
            FEEL=feel
        )

        code = protocol_base.IRCode(
            self,
            [packet[:]],
            [packet[:]],
            params
        )
        return code


Carrier = Carrier()
