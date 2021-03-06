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


TIMING = 550


class IODATAn(protocol_base.IrProtocolBase):
    """
    IR decoder for the IODATAn protocol.
    """
    irp = '{38k,550,lsb}<1,-1|1,-3>(16,-8,x:7,D:7,S:7,y:7,F:8,C:4,1,^108m)*'
    frequency = 38000
    bit_count = 40
    encoding = 'lsb'

    _lead_in = [TIMING * 16, -TIMING * 8]
    _lead_out = [TIMING, 108000]
    _middle_timings = []
    _bursts = [[TIMING, -TIMING], [TIMING, -TIMING * 3]]

    _repeat_lead_in = []
    _repeat_lead_out = []
    _repeat_bursts = []

    _code_order = [
        ['X', 7],
        ['D', 7],
        ['S', 7],
        ['Y', 7],
        ['F', 8],
        ['E', 4]
    ]

    _parameters = [
        ['X', 0, 6],
        ['D', 7, 13],
        ['S', 14, 20],
        ['Y', 21, 27],
        ['F', 28, 35],
        ['E', 36, 39],
    ]
    # [D:0..127,S:0..127,F:0..255,C:0..15=0,x:0..127=0,y:0..127=0]
    encode_parameters = [
        ['device', 0, 127],
        ['sub_device', 0, 127],
        ['function', 0, 255],
        ['extended_function', 0, 15],
        ['x', 0, 127],
        ['y', 0, 127]
    ]

    def encode(self, device, sub_device, function, extended_function, x, y, repeat_count=0):
        packet = self._build_packet(
            list(self._get_timing(x, i) for i in range(7)),
            list(self._get_timing(device, i) for i in range(7)),
            list(self._get_timing(sub_device, i) for i in range(7)),
            list(self._get_timing(y, i) for i in range(7)),
            list(self._get_timing(function, i) for i in range(8)),
            list(self._get_timing(extended_function, i) for i in range(4)),
        )

        params = dict(
            frequency=self.frequency,
            D=device,
            S=sub_device,
            F=function,
            E=extended_function,
            X=x,
            Y=y
        )

        code = protocol_base.IRCode(
            self,
            [packet[:]],
            [packet[:]],
            params,
            repeat_count
        )

        return code

    def _test_decode(self):
        rlc = [[
            8800, -4400, 550, -550, 550, -1650, 550, -550, 550, -550, 550, -1650, 550, -550, 550, -550, 550, -550,
            550, -1650, 550, -550, 550, -550, 550, -550, 550, -550, 550, -550, 550, -1650, 550, -550, 550, -550,
            550, -1650, 550, -1650, 550, -550, 550, -550, 550, -550, 550, -550, 550, -550, 550, -1650, 550, -1650,
            550, -1650, 550, -1650, 550, -550, 550, -1650, 550, -1650, 550, -550, 550, -1650, 550, -550, 550, -550,
            550, -550, 550, -1650, 550, -1650, 550, -550, 550, -550, 550, -33750
        ]]

        params = [dict(device=2, c=3, function=22, sub_device=25, x=18, y=120)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(device=2, c=3, function=22, sub_device=25, x=18, y=120)
        protocol_base.IrProtocolBase._test_encode(self, params)


IODATAn = IODATAn()
