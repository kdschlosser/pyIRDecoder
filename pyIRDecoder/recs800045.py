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


TIMING = 158


class RECS800045(protocol_base.IrProtocolBase):
    """
    IR decoder for the RECS800045 protocol.
    """
    irp = '{38k,158,msb}<1,-31|1,-47>(1:1,T:1,D:3,F:6,1,-45m)*'
    frequency = 38000
    bit_count = 11
    encoding = 'msb'

    _lead_in = []
    _lead_out = [TIMING, -45000]
    _middle_timings = []
    _bursts = [[TIMING, -TIMING * 31], [TIMING, -TIMING * 47]]

    _repeat_lead_in = []
    _repeat_lead_out = []
    _repeat_bursts = []

    _parameters = [
        ['C0', 0, 0],
        ['T', 1, 1],
        ['D', 2, 4],
        ['F', 5, 10],
    ]
    # [D:0..7,F:0..63,T@:0..1=0]
    encode_parameters = [
        ['device', 0, 7],
        ['function', 0, 63],
        ['toggle', 0, 1]
    ]

    def decode(self, data, frequency=0):
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)

        if code.c0 != 1:
            raise DecodeError('Checksum failed')

        return code

    def encode(self, device, function, toggle):
        c0 = 1

        packet = self._build_packet(
            list(self._get_timing(c0, i) for i in range(1)),
            list(self._get_timing(toggle, i) for i in range(1)),
            list(self._get_timing(device, i) for i in range(3)),
            list(self._get_timing(function, i) for i in range(6)),
        )

        return [packet]

    def _test_decode(self):
        rlc = [[
            158, -7426, 158, -4898, 158, -4898, 158, -7426, 158, -7426, 158, -7426, 158, -4898, 
            158, -7426, 158, -4898, 158, -4898, 158, -7426, 158, -45000, 
        ]]

        params = [dict(function=41, toggle=0, device=3)]

        protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(function=41, toggle=0, device=3)
        protocol_base.IrProtocolBase._test_encode(self, params)


RECS800045 = RECS800045()
