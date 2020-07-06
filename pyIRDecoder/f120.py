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

TIMING = 422


class F120(protocol_base.IrProtocolBase):
    """
    IR decoder for the F120 protocol.
    """
    irp = '{37.9k,422,lsb}<1,-3|3,-1>(D:3,H:1,F:8,-34,D:3,H:1,F:8){H=0}'
    frequency = 37900
    bit_count = 24
    encoding = 'lsb'

    _lead_in = []
    _lead_out = []
    _middle_timings = [-TIMING * 34]
    _bursts = [[TIMING, -TIMING * 3], [TIMING * 3, -TIMING]]

    _repeat_lead_in = []
    _repeat_lead_out = []
    _repeat_bursts = []

    _parameters = [
        ['D', 0, 2],
        ['H', 3, 3],
        ['F', 4, 11],
        ['D1', 12, 14],
        ['H1', 15, 15],
        ['F1', 16, 23]
    ]
    # [D:0..7,F:0..255]
    encode_parameters = [
        ['device', 0, 7],
        ['function', 0, 255]
    ]

    def decode(self, data, frequency=0):
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)

        if (
            code.device != code.d1 or
            code.h != 0 != code.h1 or
            code.function != code.f1
        ):
            raise DecodeError('Invalid checksum')

        return code

    def encode(self, device, function):
        h = 0

        packet = self._build_packet(
            list(self._get_timing(device, i) for i in range(3)),
            list(self._get_timing(h, i) for i in range(1)),
            list(self._get_timing(function, i) for i in range(8)),
            self._middle_timings,
            list(self._get_timing(device, i) for i in range(3)),
            list(self._get_timing(h, i) for i in range(1)),
            list(self._get_timing(function, i) for i in range(8))
        )

        return [packet]

    def _test_decode(self):
        rlc = [
            [
                +1266, -422, +422, -1266, +1266, -422, +422, -1266, +422, -1266, +422, -1266, +422, -1266, +1266, -422,
                +1266, -422, +1266, -422, +422, -1266, +422, -15614, +1266, -422, +422, -1266, +1266, -422, +422, -1266,
                +422, -1266, +422, -1266, +422, -1266, +1266, -422, +1266, -422, +1266, -422, +422, -1266, +422, -1266
            ]
        ]

        params = [dict(device=5, function=56)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(device=5, function=56)
        protocol_base.IrProtocolBase._test_encode(self, params)


F120 = F120()
