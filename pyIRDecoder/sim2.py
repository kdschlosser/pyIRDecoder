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


TIMING = 400


class SIM2(protocol_base.IrProtocolBase):
    """
    IR decoder for the SIM2 protocol.
    """
    irp = '{38.8k,400,lsb}<3,-3|3,-7>(6,-7,D:8,F:8,3,^115m)'
    frequency = 38800
    bit_count = 16
    encoding = 'lsb'

    _lead_in = [TIMING * 6, -TIMING * 7]
    _lead_out = [TIMING * 3, 115000]
    _middle_timings = []
    _bursts = [[TIMING * 3, -TIMING * 3], [TIMING * 3, -TIMING * 7]]

    _code_order = [
        ['D', 8],
        ['F', 8],
    ]

    _parameters = [
        ['D', 0, 7],
        ['F', 8, 15]
    ]
    # [D:0..255=236,F:0..255]
    encode_parameters = [
        ['device', 0, 255],
        ['function', 0, 255],
    ]

    def encode(self, device, function, repeat_count=0):

        packet = self._build_packet(
            list(self._get_timing(device, i) for i in range(8)),
            list(self._get_timing(function, i) for i in range(8)),
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
            2400, -2800, 1200, -2800, 1200, -2800, 1200, -2800, 1200, -2800, 1200, -1200, 
            1200, -1200, 1200, -1200, 1200, -1200, 1200, -2800, 1200, -2800, 1200, -2800, 
            1200, -1200, 1200, -2800, 1200, -1200, 1200, -2800, 1200, -2800, 1200, -54200, 
        ]]

        params = [dict(device=15, function=215)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(device=15, function=215)
        protocol_base.IrProtocolBase._test_encode(self, params)


SIM2 = SIM2()
