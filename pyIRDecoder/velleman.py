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
from . import DecodeError, RepeatLeadOut


class Velleman(protocol_base.IrProtocolBase):
    """
    IR decoder for the Velleman protocol.
    """
    irp = '{38k,msb}<700,-5060|700,-7590>(1:1,T:1,D:3,F:6,700,-55m)*'
    frequency = 38000
    bit_count = 11
    encoding = 'msb'

    _lead_in = []
    _lead_out = [700, -55000]
    _middle_timings = []
    _bursts = [[700, -5060], [700, -7590]]

    _has_repeat_lead_out = True

    _code_order = [
        ['D', 3],
        ['F', 6],
    ]

    _parameters = [
        ['C0', 0, 0],
        ['T', 1, 1],
        ['D', 2, 4],
        ['F', 5, 10]
    ]
    # [D:0..7,F:0..63,T@:0..1=0]
    encode_parameters = [
        ['device', 0, 7],
        ['function', 0, 63]
    ]

    def decode(self, data, frequency=0):
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)
        if self._last_code is not None:
            if (
                self._last_code == code and
                self._last_code.toggle == code.toggle
            ):
                return self._last_code

            last_code = self._last_code
            self._last_code.repeat_timer.stop()

            if last_code == code:
                raise RepeatLeadOut

            self._last_code = None

        if code.c0 != 1:
            raise DecodeError('Checksum failed')

        self._last_code = code
        return code

    def encode(self, device, function, repeat_count=0):
        c0 = 1
        toggle = 0

        code = self._build_packet(
            list(self._get_timing(c0, i) for i in range(1)),
            list(self._get_timing(toggle, i) for i in range(1)),
            list(self._get_timing(device, i) for i in range(3)),
            list(self._get_timing(function, i) for i in range(5)),
        )

        toggle = 1

        lead_out = self._build_packet(
            list(self._get_timing(c0, i) for i in range(1)),
            list(self._get_timing(toggle, i) for i in range(1)),
            list(self._get_timing(device, i) for i in range(3)),
            list(self._get_timing(function, i) for i in range(5)),
        )

        packet = [code] * (repeat_count + 1)
        packet += [lead_out]

        params = dict(
            frequency=self.frequency,
            D=device,
            F=function,
        )

        code = protocol_base.IRCode(
            self,
            [code[:], lead_out[:]],
            packet[:],
            params,
            repeat_count
        )

        return code

    def _test_decode(self):
        rlc = [
            [
                +700, -7590, +700, -5060, +700, -7590, +700, -5060, +700, -7590, +700, -5060, +700, -5060, +700, -5060,
                +700, -5060, +700, -7590, +700, -7590, +700, -55000
            ]
        ]

        params = [dict(function=3, toggle=0, device=5)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(function=3, toggle=0, device=5)
        protocol_base.IrProtocolBase._test_encode(self, params)


Velleman = Velleman()
