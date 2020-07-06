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


TIMING = 250


class CanalSat(protocol_base.IrProtocolBase):
    """
    IR decoder for the CanalSat protocol.
    """
    irp = '{55.5k,250,msb}<-1,1|1,-1>(T=0,(1,-1,D:7,S:6,T:1,0:1,F:7,-89m,T=1)+)'
    frequency = 55500
    bit_count = 22
    encoding = 'msb'

    _lead_in = [TIMING, -TIMING]
    _lead_out = [-89000]
    _middle_timings = []
    _bursts = [[-TIMING, TIMING], [TIMING, -TIMING]]

    _repeat_lead_in = []
    _repeat_lead_out = []
    _repeat_bursts = []

    _parameters = [
        ['D', 0, 6],
        ['S', 7, 12],
        ['T', 13, 13],
        ['C0', 14, 14],
        ['F', 15, 21],
    ]
    # [D:0..127,S:0..63,F:0..127]
    encode_parameters = [
        ['device', 0, 127],
        ['sub_device', 0, 62],
        ['function', 0, 127],
    ]

    def decode(self, data, frequency=0):
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)

        if code.c0 != 0:
            raise DecodeError('Checksum failed')

        return code

    def encode(self, device, sub_device, function):
        toggle = 0
        c0 = 0

        packet = self._build_packet(
            list(self._get_timing(device, i) for i in range(7)),
            list(self._get_timing(sub_device, i) for i in range(6)),
            list(self._get_timing(toggle, i) for i in range(1)),
            list(self._get_timing(c0, i) for i in range(1)),
            list(self._get_timing(function, i) for i in range(7)),
        )

        return [packet]

    def _test_decode(self):
        rlc = [[
            250, -500, 250, -250, 250, -250, 250, -250, 250, -250, 500, -250, 250, -250, 250, -250,
            250, -500, 500, -500, 250, -250, 250, -250, 250, -250, 500, -250, 250, -250, 250, -250,
            250, -250, 250, -250, 250, -500, 250, -89000,
        ]]

        params = [dict(device=3, function=126, sub_device=52)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(device=3, function=126, sub_device=52)
        protocol_base.IrProtocolBase._test_encode(self, params)


CanalSat = CanalSat()
