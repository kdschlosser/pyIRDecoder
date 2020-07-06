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


TIMING = 358


class Elunevision(protocol_base.IrProtocolBase):
    """
    IR decoder for the Elunevision protocol.
    """
    irp = '{0k,358,msb}<1,-3|3,-1>(10,-3,D:24,F:8,-7)*{D=0xf48080}'
    frequency = 0
    bit_count = 32
    encoding = 'msb'

    _lead_in = [TIMING * 10, -TIMING * 3]
    _lead_out = [-TIMING * 7]
    _middle_timings = []
    _bursts = [[TIMING, -TIMING * 3], [TIMING * 3, -TIMING]]

    _repeat_lead_in = []
    _repeat_lead_out = []
    _repeat_bursts = []

    _parameters = [
        ['D', 0, 23],
        ['F', 24, 31],
    ]
    # [F:0..255]
    encode_parameters = [
        ['function', 0, 255],
    ]

    def decode(self, data, frequency=0):
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)

        if code.device != 0xF48080:
            raise DecodeError('Incorrect device')

        return code

    def encode(self, function):
        device = 0xF48080

        packet = self._build_packet(
            list(self._get_timing(device, i) for i in range(24)),
            list(self._get_timing(function, i) for i in range(8)),
        )

        return [packet]

    def _test_decode(self):
        rlc = [[
            3580, -1074, 1074, -358, 1074, -358, 1074, -358, 1074, -358, 358, -1074, 1074, -358, 358, -1074,
            358, -1074, 1074, -358, 358, -1074, 358, -1074, 358, -1074, 358, -1074, 358, -1074, 358, -1074,
            358, -1074, 1074, -358, 358, -1074, 358, -1074, 358, -1074, 358, -1074, 358, -1074, 358, -1074,
            358, -1074, 358, -1074, 1074, -358, 1074, -358, 358, -1074, 1074, -358, 1074, -358, 1074, -358,
            358, -3580
        ]]

        params = [dict(function=110)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(function=110)
        protocol_base.IrProtocolBase._test_encode(self, params)


Elunevision = Elunevision()
