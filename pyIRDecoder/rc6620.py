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


TIMING = 444


class RC6620(protocol_base.IrProtocolBase):
    """
    IR decoder for the RC6620 protocol.
    """

    irp = '{36k,444,msb}<-1,1|1,-1>(6,-2,1:1,6:3,<-2,2|2,-2>(1-(T:1)),D:8,S:4,F:8,-100m)*'
    frequency = 36000
    bit_count = 25
    encoding = 'msb'

    _lead_in = [TIMING * 6, -TIMING * 2]
    _lead_out = [-100000]
    _middle_timings = [{'start': 4, 'stop': 5, 'bursts': [[-TIMING * 2, TIMING * 2], [TIMING * 2, -TIMING * 2]]}]
    _bursts = [[-TIMING, TIMING], [TIMING, -TIMING]]

    _repeat_lead_in = []
    _repeat_lead_out = []
    _repeat_bursts = []

    _parameters = [
        ['C0', 0, 0],
        ['C1', 1, 3],
        ['T', 4, 4],
        ['D', 5, 12],
        ['S', 13, 16],
        ['F', 17, 24],
    ]
    # [D:0..255,S:0..15,F:0..255,T@:0..1=0]
    encode_parameters = [
        ['device', 0, 255],
        ['sub_device', 0, 15],
        ['function', 0, 255],
        ['toggle', 0, 1]
    ]

    def decode(self, data, frequency=0):
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)

        if code.c0 != 1 or code.c1 != 6:
            raise DecodeError('Checksum failed')

        return code

    def encode(self, device, sub_device, function, toggle):
        c0 = 1
        c1 = 6

        toggle = int(not toggle)
        t_bursts = [[-TIMING * 2, TIMING * 2], [TIMING * 2, -TIMING * 2]]

        toggle = t_bursts[toggle]

        packet = self._build_packet(
            list(self._get_timing(c0, i) for i in range(1)),
            list(self._get_timing(c1, i) for i in range(3)),
            toggle,
            list(self._get_timing(device, i) for i in range(8)),
            list(self._get_timing(sub_device, i) for i in range(4)),
            list(self._get_timing(function, i) for i in range(8)),

        )

        return [packet]

    def _test_decode(self):
        rlc = [[
            2664, -888, 444, -444, 444, -444, 444, -888, 1332, -888, 444, -888, 444, -444,
            444, -444, 888, -888, 888, -888, 444, -444, 888, -888, 888, -888, 444, -444, 888, -888,
            888, -888, 444, -444, 444, -444, 444, -100000,
        ]]

        params = [dict(function=40, toggle=1, device=138, sub_device=5)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(function=40, toggle=1, device=138, sub_device=5)
        protocol_base.IrProtocolBase._test_encode(self, params)


RC6620 = RC6620()