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


TIMING = 417


class GwtS(protocol_base.IrProtocolBase):
    """
    IR decoder for the GwtS protocol.
    """
    irp = '{38.005k,417,lsb}<1|-1>(0:1,D:8,1:2,F:8,1:2,CRC:8,1:1)'
    frequency = 38005
    bit_count = 30
    encoding = 'lsb'

    _lead_in = []
    _lead_out = []
    _middle_timings = []
    _bursts = [TIMING, -TIMING]

    _repeat_lead_in = []
    _repeat_lead_out = []
    _repeat_bursts = []

    _parameters = [
        ['C0', 0, 0],
        ['D', 1, 8],
        ['C1', 9, 10],
        ['F', 11, 18],
        ['C2', 19, 20],
        ['CRC', 21, 28],
        ['C3', 29, 29]
    ]
    # [D:0..255=144,F:0..255,CRC:0..255]
    encode_parameters = [
        ['device', 0, 255],
        ['function', 0, 255],
        ['crc', 0, 255]
    ]

    def decode(self, data, frequency=0):
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)

        if code.c0 != 0 or code.c1 != 1 or code.c2 != 1 or code.c3 != 1:
            raise DecodeError('Checksum failed')

        return code

    def encode(self, device, function, crc):
        c0 = 0
        c1 = 1
        c2 = 1
        c3 = 1

        packet = self._build_packet(
            list(self._get_timing(c0, i) for i in range(1)),
            list(self._get_timing(device, i) for i in range(8)),
            list(self._get_timing(c1, i) for i in range(2)),
            list(self._get_timing(function, i) for i in range(8)),
            list(self._get_timing(c2, i) for i in range(2)),
            list(self._get_timing(crc, i) for i in range(8)),
            list(self._get_timing(c3, i) for i in range(1)),
        )
        return [packet]

    def _test_decode(self):
        rlc = [[+417, -2085, +834, -834, +1251, -417, +2085, -417, +417, -417, +2085, -1251]]

        params = [dict(device=159, function=4, crc=193)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(device=159, function=4, crc=193)
        protocol_base.IrProtocolBase._test_encode(self, params)


GwtS = GwtS()

