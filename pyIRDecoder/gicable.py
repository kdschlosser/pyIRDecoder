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

# Local imports
from . import protocol_base
from . import DecodeError


TIMING = 490


class GICable(protocol_base.IrProtocolBase):
    """
    IR decoder for the GICable protocol.
    """
    irp = '{38.7k,490,lsb}<1,-4.5|1,-9>(18,-9,F:8,D:4,C:4,1,-84,(18,-4.5,1,-178)*){C=-(D+F:4+F:4:4)}'
    frequency = 38700
    bit_count = 16
    encoding = 'lsb'

    _lead_in = [TIMING * 18, -TIMING * 9]
    _lead_out = [TIMING, -TIMING * 84]
    _middle_timings = []
    _bursts = [[TIMING, int(round(-TIMING * 4.5))], [TIMING, -TIMING * 9]]

    _repeat_lead_in = [TIMING * 18, int(round(-TIMING * 4.5))]
    _repeat_lead_out = [TIMING, -TIMING * -178]
    _repeat_bursts = []

    _code_order = [
        ['F', 8],
        ['D', 4]
    ]

    _parameters = [
        ['F', 0, 7],
        ['D', 8, 11],
        ['CHECKSUM', 12, 15]
    ]
    # [D:0..15,F:0..255]
    # TODO: get this protocol working with the bottom 7 device ID's. It uses Hamming to make up the bit.
    encode_parameters = [
        ['device', 7, 15],
        ['function', 0, 255],
    ]

    def _calc_checksum(self, device, function):
        # -(D+F:4+F:4:4)
        f1 = self._get_bits(function, 0, 3)
        f2 = self._get_bits(function, 4, 7)

        c = -(device + f1 + f2)
        return self._get_bits(c, 0, 3)

    def decode(self, data, frequency=0):
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)
        if self._last_code is not None:
            if self._last_code == code:
                return self._last_code

            self._last_code.repeat_timer.stop()
            self._last_code = None

        checksum = self._calc_checksum(code.device, code.function)

        if checksum != code.checksum:
            raise DecodeError('Checksum failed')

        self._last_code = code
        return code

    def encode(self, device, function, repeat_count=0):
        checksum = self._calc_checksum(device, function)

        packet = self._build_packet(
            list(self._get_timing(function, i) for i in range(8)),
            list(self._get_timing(device, i) for i in range(4)),
            list(self._get_timing(checksum, i) for i in range(4))
        )

        params = dict(
            frequency=self.frequency,
            D=device,
            F=function,
        )

        code = protocol_base.IRCode(
            self,
            [packet[:]],
            [packet[:]] + self._build_repeat_packet(repeat_count),
            params,
            repeat_count
        )
        return code

    def _test_decode(self):
        rlc = [[
            8820, -4410, 490, -2205, 490, -2205, 490, -2205, 490, -4410, 490, -2205, 490, -4410, 490, -4410,
            490, -4410, 490, -2205, 490, -2205, 490, -2205, 490, -2205, 490, -2205, 490, -4410, 490, -2205,
            490, -4410, 490, -41160
        ]]

        params = [dict(device=0, function=232)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(device=0, function=232)
        protocol_base.IrProtocolBase._test_encode(self, params)


GICable = GICable()
