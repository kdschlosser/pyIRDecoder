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


TIMING = 500


class Bose(protocol_base.IrProtocolBase):
    """
    IR decoder for the Bose protocol.
    """
    irp = '{38.0k,500,msb}<1,-1|1,-3>(2,-3,F:8,~F:8,1,-50m)*'
    frequency = 38000
    bit_count = 16
    encoding = 'msb'

    _lead_in = [TIMING * 2, -TIMING * 3]
    _lead_out = [TIMING, -50000]
    _middle_timings = []
    _bursts = [[TIMING, -TIMING], [TIMING, -TIMING * 3]]

    _repeat_lead_in = []
    _repeat_lead_out = []
    _repeat_bursts = []

    _parameters = [
        ['F', 0, 7],
        ['F_CHECKSUM', 8, 15],
    ]
    # [F:0..255]
    encode_parameters = [
        ['function', 0, 255],
    ]

    def _calc_checksum(self, function):
        f = self._invert_bits(function, 8)
        return f

    def decode(self, data, frequency=0):
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)
        func_checksum = self._calc_checksum(code.function)

        if func_checksum != code.f_checksum:
            raise DecodeError('Checksum failed')

        return code

    def encode(self, function):
        func_checksum = self._calc_checksum(function)
        packet = self._build_packet(
            list(self._get_timing(function, i) for i in range(8)),
            list(self._get_timing(func_checksum, i) for i in range(8)),
        )

        return [packet]

    def _test_decode(self):
        rlc = [[
            1000, -1500, 500, -500, 500, -1500, 500, -1500, 500, -1500, 500, -500, 500, -1500,
            500, -1500, 500, -500, 500, -1500, 500, -500, 500, -500, 500, -500, 500, -1500,
            500, -500, 500, -500, 500, -1500, 500, -50000,
        ]]

        params = [dict(function=118)]

        protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(function=118)
        protocol_base.IrProtocolBase._test_encode(self, params)


Bose = Bose()
