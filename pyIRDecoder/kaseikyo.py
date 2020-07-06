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


class Kaseikyo(protocol_base.IrProtocolBase):
    """
    IR decoder for the Kaseikyo protocol.
    """
    irp = (
        '{37k,432,lsb}<1,-1|1,-3>(8,-4,M:8,N:8,X:4,D:4,S:8,F:8,E:4,C:4,1,-173)*'
        '{X=((M^N)::4)^(M^N),chksum=D^S^F^(E*16),C=chksum::4^chksum}'
    )
    frequency = 37000
    bit_count = 48
    encoding = 'lsb'

    _lead_in = [TIMING * 8, -TIMING * 4]
    _lead_out = [TIMING, -TIMING * 173]
    _middle_timings = []
    _bursts = [[TIMING, -TIMING], [TIMING, -TIMING * 3]]

    _repeat_lead_in = []
    _repeat_lead_out = []
    _repeat_bursts = []

    _parameters = [
        ['M', 0, 7],
        ['N', 8, 15],
        ['X', 16, 19],
        ['D', 20, 23],
        ['S', 24, 31],
        ['F', 32, 39],
        ['E', 40, 43],
        ['CHECKSUM', 44, 47]
    ]
    # [D:0..15,S:0..255,F:0..255,E:0..15,M:0..255,N:0..255]
    encode_parameters = [
        ['device', 0, 15],
        ['sub_device', 0, 255],
        ['function', 0, 255],
        ['extended_function', 0, 15],
        ['mode', 0, 255],
        ['n', 0, 255]
    ]

    def _calc_checksum(self, mode, n, device, sub_device, function, extended_function):
        x = ((mode ^ n) >> 4) ^ (mode ^ n)
        checksum = device ^ sub_device ^ function ^ (extended_function * 16)
        checksum = checksum >> 4 ^ checksum

        return self._get_bits(x, 0, 3), self._get_bits(checksum, 0, 3)

    def decode(self, data, frequency=0):
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)
        x, checksum = self._calc_checksum(
            code.mode,
            code.n,
            code.device,
            code.sub_device,
            code.function,
            code.extended_function
        )

        if x != code.x or checksum != code.checksum:
            raise DecodeError('Checksum failed')

        return code

    def encode(self, mode, n, device, sub_device, function, extended_function):
        x, checksum = self._calc_checksum(
            mode, n, device, sub_device, function, extended_function
        )

        packet = self._build_packet(
            list(self._get_timing(mode, i) for i in range(8)),
            list(self._get_timing(n, i) for i in range(8)),
            list(self._get_timing(x, i) for i in range(4)),
            list(self._get_timing(device, i) for i in range(4)),
            list(self._get_timing(sub_device, i) for i in range(8)),
            list(self._get_timing(function, i) for i in range(8)),
            list(self._get_timing(extended_function, i) for i in range(4)),
            list(self._get_timing(checksum, i) for i in range(4))
        )

        return [packet]

    def _test_decode(self):
        rlc = [[
            3456, -1728, 432, -1296, 432, -432, 432, -432, 432, -1296, 432, -1296, 432, -432, 432, -1296,
            432, -1296, 432, -432, 432, -432, 432, -1296, 432, -432, 432, -1296, 432, -1296, 432, -1296,
            432, -1296, 432, -1296, 432, -1296, 432, -1296, 432, -1296, 432, -1296, 432, -432, 432, -1296,
            432, -432, 432, -1296, 432, -1296, 432, -432, 432, -432, 432, -432, 432, -432, 432, -432, 432, -1296,
            432, -432, 432, -432, 432, -432, 432, -432, 432, -432, 432, -432, 432, -1296, 432, -1296, 432, -432,
            432, -1296, 432, -1296, 432, -1296, 432, -432, 432, -432, 432, -1296, 432, -1296, 432, -74736
        ]]

        params = [dict(device=5, extended_function=14, function=192, mode=217, n=244, sub_device=131)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(device=5, extended_function=14, function=192, mode=217, n=244, sub_device=131)
        protocol_base.IrProtocolBase._test_encode(self, params)


Kaseikyo = Kaseikyo()
