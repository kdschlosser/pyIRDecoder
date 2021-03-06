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


TIMING = 2300


# TODO: Finish
class Lutron(protocol_base.IrProtocolBase):
    """
    IR decoder for the Lutron protocol.
    """
    irp = '{40k,2300,msb}<-1|1>(255:8,X:24,0:4)*'
    frequency = 40000
    bit_count = 36
    encoding = 'msb'

    _bursts = [-TIMING, TIMING]

    _code_order = [
        ['X', 24],
    ]

    _parameters = [
        ['C0', 0, 7],
        ['X', 8, 31],
        ['C1', 32, 35],
    ]
    # [X:0..16777215]
    encode_parameters = [
        ['x', 0, 16777215]
    ]

    def decode(self, data, frequency=0):
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)
        if self._last_code is not None:
            if self._last_code == code:
                return self._last_code

            self._last_code.repeat_timer.stop()
            self._last_code = None

        if code.c0 != 255 or code.c1 != 0:
            raise DecodeError('Checksum failed')

        self._last_code = code
        return code

    def encode(self, x, repeat_count=0):
        c0 = 255
        c1 = 0

        packet = self._build_packet(
            list(self._get_timing(c0, i) for i in range(8)),
            list(self._get_timing(x, i) for i in range(24)),
            list(self._get_timing(c1, i) for i in range(4))
        )

        params = dict(
            frequency=self.frequency,
            X=x
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
            23000, -6900, 2300, -9200, 4600, -4600, 2300, -2300, 4600, -4600, 2300, -16100,
        ]]

        params = [dict(x=12858056)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(x=12858056)
        protocol_base.IrProtocolBase._test_encode(self, params)


Lutron = Lutron()
