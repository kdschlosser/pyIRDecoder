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


TIMING = 500


class Konka(protocol_base.IrProtocolBase):
    """
    IR decoder for the Konka protocol.
    """
    irp = '{38k,500,msb}<1,-3|1,-5>(6,-6,D:8,F:8,1,-8,1,-46)*'
    frequency = 38000
    bit_count = 16
    encoding = 'msb'

    _lead_in = [TIMING * 6, -TIMING * 6]
    _lead_out = [TIMING, -TIMING * 8, TIMING, -TIMING * 46]
    _middle_timings = []
    _bursts = [[TIMING, -TIMING * 3], [TIMING, -TIMING * 5]]

    _code_order = [
        ['D', 8],
        ['F', 8],
    ]

    _parameters = [
        ['D', 0, 7],
        ['F', 8, 15],
    ]
    # [D:0..255,F:0..255]
    encode_parameters = [
        ['device', 0, 255],
        ['function', 0, 255],
    ]

    def encode(self, device, function, repeat_count=0):
        packet = self._build_packet(
            list(self._get_timing(device, i) for i in range(8)),
            list(self._get_timing(function, i) for i in range(8))
        )

        params = dict(
            frequency=self.frequency,
            D=device,
            F=function,
        )

        code = protocol_base.IRCode(
            self,
            [packet[:]],
            [packet[:]] * (repeat_count + 1),
            params,
            repeat_count
        )

        return code

    def _test_decode(self):
        rlc = [[
            3000, -3000, 500, -1500, 500, -1500, 500, -2500, 500, -1500, 500, -1500, 500, -1500, 500, -2500,
            500, -1500, 500, -1500, 500, -1500, 500, -1500, 500, -2500, 500, -1500, 500, -2500, 500, -2500,
            500, -2500, 500, -4000, 500, -23000
        ]]

        params = [dict(device=34, function=23)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(device=186, function=189)
        protocol_base.IrProtocolBase._test_encode(self, params)


Konka = Konka()
