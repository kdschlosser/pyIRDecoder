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


TIMING = 1


class PID0001(protocol_base.IrProtocolBase):
    """
    IR decoder for the PID0001 protocol.
    """
    irp = '{0k,1,msb}<24,-9314|24,-13486>(24,-21148,(F:5,1,-28m)+)'
    frequency = 0
    bit_count = 5
    encoding = 'msb'

    _lead_in = [24, -21148]
    _lead_out = [1, -28000]
    _middle_timings = []
    _bursts = [[24, -9314], [24, -13486]]

    _repeat_lead_in = []
    _repeat_lead_out = []
    _repeat_bursts = []

    _parameters = [
        ['F', 0, 4],
    ]
    # [F:0..31]
    encode_parameters = [
        ['function', 0, 31],
    ]

    def encode(self, function):
        packet = self._build_packet(
            list(self._get_timing(function, i) for i in range(5))
        )

        return [packet]

    def _test_decode(self):
        rlc = [[
            24, -21148, 24, -13486, 24, -9314, 24, -13486, 24, -13486, 24, -9314, 1, -28000,
        ]]

        params = [dict(function=22)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(function=22)
        protocol_base.IrProtocolBase._test_encode(self, params)


PID0001 = PID0001()