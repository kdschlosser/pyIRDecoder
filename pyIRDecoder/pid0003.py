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


TIMING = 389


class PID0003(protocol_base.IrProtocolBase):
    """
    IR decoder for the PID0003 protocol.
    """
    irp = '{40.2k,389,lsb}<2,-2|3,-1>(F:8,~F:8,^102m)*'
    frequency = 40200
    bit_count = 16
    encoding = 'lsb'

    _lead_in = []
    _lead_out = [102000]
    _middle_timings = []
    _bursts = [[TIMING * 2, -TIMING * 2], [TIMING * 3, -TIMING]]

    _code_order = [
        ['F', 8],
    ]

    _parameters = [
        ['F', 0, 7],
        ['CHECKSUM', 8, 15],
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

        if self._last_code is not None:
            if self._last_code == code:
                return self._last_code

            self._last_code.repeat_timer.stop()
            self._last_code = None

        checksum = self._calc_checksum(code.function)

        if checksum != code.checksum:
            raise DecodeError('Checksum failed')

        self._last_code = code
        return code

    def encode(self, function, repeat_count=0):
        checksum = self._calc_checksum(function)

        packet = self._build_packet(
            list(self._get_timing(function, i) for i in range(8)),
            list(self._get_timing(checksum, i) for i in range(8))
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
            1167, -389, 1167, -389, 1167, -389, 1167, -389, 1167, -389, 778, -778, 1167, -389, 
            778, -778, 778, -778, 778, -778, 778, -778, 778, -778, 778, -778, 1167, -389, 
            778, -778, 1167, -77493, 
        ]]

        params = [dict(function=95)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(function=95)
        protocol_base.IrProtocolBase._test_encode(self, params)


PID0003 = PID0003()
