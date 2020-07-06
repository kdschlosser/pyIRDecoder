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


TIMING = 432


class MitsubishiK(protocol_base.IrProtocolBase):
    """
    IR decoder for the MitsubishiK protocol.
    """
    irp = '{37k,432,lsb}<1,-1|1,-3>(8,-4,35:8,203:8,X:4,D:8,S:8,F:8,T:4,1,-100)*{X=6,T=-S:4:0-S:4:4-F:4:0-F:4:4+15}'
    frequency = 37000
    bit_count = 48
    encoding = 'lsb'

    _lead_in = [TIMING * 8, -TIMING * 4]
    _lead_out = [TIMING, -TIMING * 100]
    _middle_timings = []
    _bursts = [[TIMING, -TIMING], [TIMING, -TIMING * 3]]

    _repeat_lead_in = []
    _repeat_lead_out = []
    _repeat_bursts = []

    _parameters = [
        ['C0', 0, 7],
        ['C1', 8, 15],
        ['X', 16, 19],
        ['D', 20, 27],
        ['S', 28, 35],
        ['F', 36, 43],
        ['CHECKSUM', 44, 47]
    ]
    # [D:0..255,F:0..255,S:0..255]
    encode_parameters = [
        ['device', 0, 255],
        ['sub_device', 0, 255],
        ['function', 0, 255],
    ]

    def _calc_checksum(self, sub_device, function):
        s1 = self._get_bits(sub_device, 0, 3)
        s2 = self._get_bits(sub_device, 4, 7)
        f1 = self._get_bits(function, 0, 3)
        f2 = self._get_bits(function, 4, 7)
        return self._get_bits(-s1 - s2 - f1 - f2 + 15, 0, 3)

    def decode(self, data, frequency=0):
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)
        checksum = self._calc_checksum(code.sub_device, code.function)

        if checksum != code.checksum or code.x != 6 or code.c0 != 35 or code.c1 != 203:
            raise DecodeError('Checksum failed')

        return code

    def encode(self, device, sub_device, function):
        c0 = 35
        c1 = 203
        x = 6
        checksum = self._calc_checksum(sub_device, function)
        
        packet = self._build_packet(
            list(self._get_timing(c0, i) for i in range(8)),
            list(self._get_timing(c1, i) for i in range(8)),
            list(self._get_timing(x, i) for i in range(4)),
            list(self._get_timing(device, i) for i in range(8)),
            list(self._get_timing(sub_device, i) for i in range(8)),
            list(self._get_timing(function, i) for i in range(8)),
            list(self._get_timing(checksum, i) for i in range(4))
        )

        return [packet]

    def _test_decode(self):
        rlc = [[
            3456, -1728, 432, -1296, 432, -1296, 432, -432, 432, -432, 432, -432, 432, -1296, 
            432, -432, 432, -432, 432, -1296, 432, -1296, 432, -432, 432, -1296, 432, -432, 
            432, -432, 432, -1296, 432, -1296, 432, -432, 432, -1296, 432, -1296, 432, -432, 
            432, -432, 432, -1296, 432, -1296, 432, -432, 432, -1296, 432, -1296, 432, -1296, 
            432, -432, 432, -1296, 432, -1296, 432, -1296, 432, -1296, 432, -432, 432, -1296, 
            432, -432, 432, -432, 432, -432, 432, -1296, 432, -432, 432, -432, 432, -432, 
            432, -1296, 432, -1296, 432, -1296, 432, -432, 432, -1296, 432, -1296, 432, -1296, 
            432, -43200, 
        ]]

        params = [dict(device=118, function=226, sub_device=47)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(device=118, function=226, sub_device=47)
        protocol_base.IrProtocolBase._test_encode(self, params)


MitsubishiK = MitsubishiK()