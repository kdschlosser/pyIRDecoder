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


TIMING = 398


class RTIRelay(protocol_base.IrProtocolBase):
    """
    IR decoder for the RTIRelay protocol.
    """
    irp = '{40.244k,398,msb}<1,-1|-1,1>(1,A:31,F:1,F:8,D:23,D:8,0:4,-19.5m)*{A=0x7fe08080}'
    frequency = 40244
    bit_count = 75
    encoding = 'msb'

    _lead_in = [TIMING]
    _lead_out = [-19500]
    _middle_timings = []
    _bursts = [[TIMING, -TIMING], [-TIMING, TIMING]]

    _code_order = [
        ['F', 1],
        ['D', 8],
    ]

    _parameters = [
        ['A', 0, 30],
        ['F', 31, 31],
        ['F1', 32, 39],
        ['D1', 40, 62],
        ['D', 63, 70],
        ['C0', 71, 74]
    ]
    # [F:0..1,D:0..255]
    encode_parameters = [
        ['device', 0, 255],
        ['function', 0, 1],
    ]

    def decode(self, data, frequency=0):
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)

        if self._last_code is not None:
            if self._last_code == code:
                return self._last_code

            self._last_code.repeat_timer.stop()
            self._last_code = None

        if code.a != 0x7FE08080 or code.c0 != 0:
            raise DecodeError('Checksum failed')

        self._last_code = code
        return code

    def encode(self, device, function, repeat_count=0):
        a = 0x7FE08080
        c0 = 0
        f1 = 0
        d1 = 0

        packet = self._build_packet(
            list(self._get_timing(a, i) for i in range(31)),
            list(self._get_timing(function, i) for i in range(1)),
            list(self._get_timing(f1, i) for i in range(8)),
            list(self._get_timing(d1, i) for i in range(23)),
            list(self._get_timing(device, i) for i in range(8)),
            list(self._get_timing(c0, i) for i in range(4)),
        )

        params = dict(
            frequency=self.frequency,
            D=device,
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
            398, -398, 398, -398, 398, -398, 398, -398, 398, -398, 398, -398, 398, -398, 398, -398, 
            398, -398, 398, -398, 796, -398, 398, -398, 398, -398, 398, -398, 398, -796, 796, -398, 
            398, -398, 398, -398, 398, -398, 398, -398, 398, -398, 398, -796, 796, -398, 398, -398, 
            398, -398, 398, -398, 398, -398, 398, -398, 398, -796, 796, -398, 398, -398, 398, -398, 
            398, -398, 398, -398, 398, -398, 398, -796, 796, -398, 398, -398, 398, -398, 398, -398, 
            398, -398, 398, -398, 398, -398, 398, -398, 398, -398, 398, -398, 398, -398, 398, -398, 
            398, -398, 398, -398, 398, -398, 398, -398, 398, -796, 398, -398, 398, -398, 796, -398, 
            398, -796, 796, -398, 398, -796, 398, -398, 398, -398, 796, -398, 398, -796, 796, -398, 
            398, -398, 398, -398, 398, -19898, 
        ]]

        params = [dict(device=57, function=1)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(device=57, function=1)
        protocol_base.IrProtocolBase._test_encode(self, params)


RTIRelay = RTIRelay()
