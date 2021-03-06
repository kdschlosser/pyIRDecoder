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


TIMING = 750


class Whynter(protocol_base.IrProtocolBase):
    """
    IR decoder for the Whynter protocol.
    """
    irp = '{38k,750,msb}<1,-1|1,-3>(0:1,4,-4,F:32,1,-50m)'
    frequency = 38000
    bit_count = 33
    encoding = 'msb'

    _lead_in = []
    _lead_out = [TIMING, -50000]
    _middle_timings = [(TIMING * 4, -TIMING * 4)]
    _bursts = [[TIMING, -TIMING], [TIMING, -TIMING * 3]]

    _code_order = [
        ['F', 32],
    ]

    _parameters = [
        ['C0', 0, 0],
        ['F', 1, 32],
    ]
    # [F:0..0xFFFFFFFF]
    encode_parameters = [
        ['function', 0, 0xFFFFFFFF]
    ]

    def decode(self, data, frequency=0):
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)

        if self._last_code is not None:
            if self._last_code == code:
                return self._last_code

            self._last_code.repeat_timer.stop()

        if code.c0 != 0:
            raise DecodeError('Invalid checksum')
        self._last_code = code
        return code

    def encode(self, function, repeat_count=0):
        c0 = 0

        packet = self._build_packet(
            list(self._get_timing(c0, i) for i in range(1)),
            self._middle_timings,
            list(self._get_timing(function, i) for i in range(32)),
        )

        params = dict(
            frequency=self.frequency,
            F=function,
        )

        code = protocol_base.IRCode(
            self,
            [packet[:]],
            [packet[:]] * (repeat_count + 1),
            params,
            repeat_count
        )

        return code

    def _test_decode(self):
        return
        rlc = [
            [
                +889, -889, +889, -889, +1778, -1778, +1778, -889, +889, -889, +889, -1778, +889, -889, +889, -889,
                +889, -889, +889, -889, +889, -889, +889, -89997
            ]
        ]

        params = [dict(function=63, toggle=1, device=8)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        return
        params = dict(function=106, toggle=1, device=11)
        protocol_base.IrProtocolBase._test_encode(self, params)


Whynter = Whynter()


