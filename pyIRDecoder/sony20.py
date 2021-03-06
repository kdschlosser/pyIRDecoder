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


TIMING = 600


class Sony20(protocol_base.IrProtocolBase):
    """
    IR decoder for the Sony20 protocol.
    """
    irp = '{40k,600,lsb}<1,-1|2,-1>(4,-1,F:7,D:5,S:8,^45m)*'
    frequency = 40000
    bit_count = 20
    encoding = 'lsb'

    _lead_in = [TIMING * 4, -TIMING]
    _lead_out = [45000]
    _middle_timings = []
    _bursts = [[TIMING, -TIMING], [TIMING * 2, -TIMING]]

    _code_order = [
        ['F', 7],
        ['D', 5],
        ['S', 8],
    ]

    _parameters = [
        ['F', 0, 6],
        ['D', 7, 11],
        ['S', 12, 19]
    ]

    # [D:0..31,S:0..255,F:0..127]
    encode_parameters = [
        ['device', 0, 31],
        ['sub_device', 0, 255],
        ['function', 0, 127],
    ]

    def encode(self, device, function, sub_device, repeat_count=0):
        packet = self._build_packet(
            list(self._get_timing(function, i) for i in range(7)),
            list(self._get_timing(device, i) for i in range(5)),
            list(self._get_timing(sub_device, i) for i in range(8))
        )

        params = dict(
            frequency=self.frequency,
            D=device,
            S=sub_device,
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
        rlc =[[
            2400, -600, 600, -600, 600, -600, 600, -600, 1200, -600, 1200, -600, 600, -600,
            600, -600, 600, -600, 1200, -600, 1200, -600, 600, -600, 600, -600, 1200, -600,
            600, -600, 600, -600, 1200, -600, 600, -600, 600, -600, 600, -600, 1200, -14400,
        ]]

        params = [dict(device=6, function=24, sub_device=137)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(device=6, function=24, sub_device=137)
        protocol_base.IrProtocolBase._test_encode(self, params)


Sony20 = Sony20()
