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


TIMING = 1000


class GIRG(protocol_base.IrProtocolBase):
    """
    IR decoder for the GIRG protocol.
    """
    irp = '{37.3k,1000,msb}<1,-1|1,-3>(5,-3,F:6,S:2,D:8,1,-60)*'
    frequency = 37300
    bit_count = 16
    encoding = 'msb'

    _lead_in = [TIMING * 5, -TIMING * 3]
    _lead_out = [TIMING, -TIMING * 60]
    _middle_timings = []
    _bursts = [[TIMING, -TIMING], [TIMING, -TIMING * 3]]

    _repeat_lead_in = []
    _repeat_lead_out = []
    _repeat_bursts = []

    _parameters = [
        ['F', 0, 5],
        ['S', 6, 7],
        ['D', 8, 15]
    ]
    # [D:0..255,S:0..3,F:0..63]
    encode_parameters = [
        ['device', 0, 255],
        ['sub_device', 0, 3],
        ['function', 0, 63],
    ]

    def encode(self, device, sub_device, function):
        packet = self._build_packet(
            list(self._get_timing(function, i) for i in range(6)),
            list(self._get_timing(sub_device, i) for i in range(2)),
            list(self._get_timing(device, i) for i in range(8)),
        )

        return [packet]

    def _test_decode(self):
        rlc = [[
            5000, -3000, 1000, -3000, 1000, -3000, 1000, -1000, 1000, -3000, 1000, -1000, 1000, -1000, 1000, -3000,
            1000, -1000, 1000, -3000, 1000, -1000, 1000, -1000, 1000, -1000, 1000, -1000, 1000, -3000, 1000, -1000,
            1000, -1000, 1000, -60000
        ]]

        params = [dict(device=132, sub_device=2, function=52)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(device=132, sub_device=2, function=52)
        protocol_base.IrProtocolBase._test_encode(self, params)


GIRG = GIRG()