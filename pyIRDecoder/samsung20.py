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


TIMING = 564


class Samsung20(protocol_base.IrProtocolBase):
    """
    IR decoder for the Samsung20 protocol.
    """
    irp = '{38.4k,564,lsb}<1,-1|1,-3>(8,-8,D:6,S:6,F:8,1,^100m)*'
    frequency = 38400
    bit_count = 20
    encoding = 'lsb'

    _lead_in = [TIMING * 8, -TIMING * 8]
    _lead_out = [TIMING, 100000]
    _middle_timings = []
    _bursts = [[TIMING, -TIMING], [TIMING, -TIMING * 3]]

    _repeat_lead_in = []
    _repeat_lead_out = []
    _repeat_bursts = []
    # D:6,S:6,F:8
    _parameters = [
        ['D', 0, 5],
        ['S', 6, 11],
        ['F', 12, 19],
    ]
    # [D:0..63,S:0..63,F:0..255]
    encode_parameters = [
        ['device', 0, 63],
        ['sub_device', 0, 63],
        ['function', 0, 255],
    ]

    def encode(self, device, sub_device, function):

        packet = self._build_packet(
            list(self._get_timing(device, i) for i in range(6)),
            list(self._get_timing(sub_device, i) for i in range(6)),
            list(self._get_timing(function, i) for i in range(8))
        )

        return [packet]

    def _test_decode(self):
        rlc = [[
            4512, -4512, 564, -564, 564, -1692, 564, -564, 564, -564, 564, -1692, 564, -564, 
            564, -1692, 564, -1692, 564, -1692, 564, -564, 564, -564, 564, -564, 564, -564, 
            564, -564, 564, -564, 564, -564, 564, -1692, 564, -1692, 564, -1692, 564, -1692, 
            564, -57700, 
        ]]

        params = [dict(device=18, function=240, sub_device=7)]

        protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(device=18, function=240, sub_device=7)
        protocol_base.IrProtocolBase._test_encode(self, params)


Samsung20 = Samsung20()
