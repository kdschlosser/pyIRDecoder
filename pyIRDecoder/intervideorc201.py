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


TIMING = 300


class InterVideoRC201(protocol_base.IrProtocolBase):
    """
    IR decoder for the InterVideoRC201 protocol.
    """
    irp = '{38k,300,lsb}<1,-1|1,-3>(10,-5,0:1,F:6,768:10,1,-10m)*'
    frequency = 38000
    bit_count = 17
    encoding = 'lsb'

    _lead_in = [TIMING * 10, -TIMING * 5]
    _lead_out = [TIMING, -10000]
    _middle_timings = []
    _bursts = [[TIMING, -TIMING], [TIMING, -TIMING * 5]]

    _code_order = [
        ['F', 6],
    ]

    _parameters = [
        ['C0', 0, 0],
        ['F', 1, 6],
        ['C1', 7, 16],
    ]
    # [F:0..63]
    encode_parameters = [
        ['function', 0, 63],
    ]

    def decode(self, data, frequency=0):
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)

        if self._last_code is not None:
            if self._last_code == code:
                return self._last_code

            self._last_code.repeat_timer.stop()
            self._last_code = None

        if code.c0 != 0 or code.c1 != 768:
            raise DecodeError('Checksum failed')

        self._last_code = code
        return code

    def encode(self, function, repeat_count=0):
        c0 = 0
        c1 = 768

        packet = self._build_packet(
            list(self._get_timing(c0, i) for i in range(1)),
            list(self._get_timing(function, i) for i in range(6)),
            list(self._get_timing(c1, i) for i in range(10))
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
        rlc = [[
            3000, -1500, 300, -300, 300, -300, 300, -300, 300, -1500, 300, -300, 300, -300, 300, -1500, 300, -300,
            300, -300, 300, -300, 300, -300, 300, -300, 300, -300, 300, -300, 300, -300, 300, -1500, 300, -1500,
            300, -10000
        ]]

        params = [dict(function=36)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(function=36)
        protocol_base.IrProtocolBase._test_encode(self, params)


InterVideoRC201 = InterVideoRC201()
