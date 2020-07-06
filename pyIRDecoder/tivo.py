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


class Tivo(protocol_base.IrProtocolBase):
    """
    IR decoder for the Tivo protocol.
    """
    irp = '{38.4k,564,lsb}<1,-1|1,-3>(16,-8,D:8,S:8,F:8,U:4,~F:4:4,1,-78,(16,-4,1,-173)*)'
    frequency = 38400
    bit_count = 32
    encoding = 'lsb'

    _lead_in = [TIMING * 16, -TIMING * 8]
    _lead_out = [TIMING, -TIMING * 78]
    _middle_timings = []
    _bursts = [[TIMING, -TIMING], [TIMING, -TIMING * 3]]

    _repeat_lead_in = [TIMING * 16, -TIMING * 4]
    _repeat_lead_out = [TIMING, -TIMING * 173]
    _repeat_bursts = []

    _parameters = [
        ['D', 0, 7],
        ['S', 8, 15],
        ['F', 16, 23],
        ['U', 24, 27],
        ['F_CHECKSUM', 28, 31]
    ]
    # [D:133..133=133,S:48..48=48,F:0..255,U:0..15]
    encode_parameters = [
        ['function', 0, 255],
        ['u', 0, 15]
    ]

    def _calc_checksum(self, function):
        f = self._invert_bits(self._get_bits(function, 4, 7), 4)
        return self._get_bits(f, 0, 3)

    def decode(self, data, frequency=0):
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)
        func_checksum = self._calc_checksum(code.function)

        if func_checksum != code.f_checksum or code.device != 133 or code.sub_device != 48:
            raise DecodeError('Checksum failed')

        return code

    def encode(self, function, u):
        device = 133
        sub_device = 48
        func_checksum = self._calc_checksum(function)

        packet = self._build_packet(
            list(self._get_timing(device, i) for i in range(8)),
            list(self._get_timing(sub_device, i) for i in range(8)),
            list(self._get_timing(function, i) for i in range(8)),
            list(self._get_timing(u, i) for i in range(4)),
            list(self._get_timing(func_checksum, i) for i in range(4)),
        )

        return [packet]

    def _test_decode(self):
        rlc = [[
            9024, -4512, 564, -1692, 564, -564, 564, -1692, 564, -564, 564, -564, 564, -564,
            564, -564, 564, -1692, 564, -564, 564, -564, 564, -564, 564, -564, 564, -1692,
            564, -1692, 564, -564, 564, -564, 564, -1692, 564, -1692, 564, -1692, 564, -564,
            564, -564, 564, -1692, 564, -1692, 564, -564, 564, -564, 564, -564, 564, -1692,
            564, -564, 564, -1692, 564, -564, 564, -564, 564, -1692, 564, -43992,
        ]]

        params = [dict(function=103, u=4, sub_device=48, device=133)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(function=103, u=4, sub_device=48, device=133)
        protocol_base.IrProtocolBase._test_encode(self, params)


Tivo = Tivo()