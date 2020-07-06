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

TIMING = 422


class F32(protocol_base.IrProtocolBase):
    """
    IR decoder for the F32 protocol.
    """
    irp = '{37.9k,422,msb}<1,-3|3,-1>(D:8,S:8,F:8,E:8,-100m)*'
    frequency = 37900
    bit_count = 32
    encoding = 'msb'

    _lead_in = []
    _lead_out = [-100000]
    _middle_timings = []
    _bursts = [[TIMING, -TIMING * 3], [TIMING * 3, -TIMING]]

    _repeat_lead_in = []
    _repeat_lead_out = []
    _repeat_bursts = []

    _parameters = [
        ['D', 0, 7],
        ['S', 8, 15],
        ['F', 16, 23],
        ['E', 24, 31]
    ]
    # [D:0..255,S:0..255,F:0..255,E:0..255]
    encode_parameters = [
        ['device', 0, 255],
        ['sub_device', 0, 255],
        ['function', 0, 255],
        ['e', 0, 255]
    ]

    def encode(self, device, sub_device, function, e):

        packet = self._build_packet(
            list(self._get_timing(device, i) for i in range(8)),
            list(self._get_timing(sub_device, i) for i in range(8)),
            list(self._get_timing(function, i) for i in range(8)),
            list(self._get_timing(e, i) for i in range(8)),
        )

        return [packet]

    def _test_decode(self):
        rlc = [[
            422, -1266, 422, -1266, 1266, -422, 1266, -422, 422, -1266, 422, -1266, 422, -1266, 422, -1266,
            1266, -422, 422, -1266, 422, -1266, 422, -1266, 1266, -422, 422, -1266, 422, -1266, 1266, -422,
            1266, -422, 1266, -422, 1266, -422, 1266, -422, 422, -1266, 422, -1266, 1266, -422, 1266, -422,
            422, -1266, 1266, -422, 1266, -422, 1266, -422, 422, -1266, 1266, -422, 1266, -422, 422, -101266
        ]]

        params = [dict(device=48, function=243, sub_device=137, e=118)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(device=48, function=243, sub_device=137, e=118)
        protocol_base.IrProtocolBase._test_encode(self, params)


F32 = F32()
