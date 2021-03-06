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
from . import (
    DecodeError,
    RepeatLeadIn,
    RepeatLeadOut,
    RepeatTimeoutExpired
)
import time

TIMING = 500


class NRC16(protocol_base.IrProtocolBase):
    """
    IR decoder for the NRC16 protocol.
    """
    irp = '{38k,500,lsb}<-1,1|1,-1>(1,-5,1:1,254:8,127:7,-15m,(1,-5,1:1,F:8,D:7,-110m)+,1,-5,1:1,254:8,127:7,-15m)'
    frequency = 38000
    bit_count = 16
    encoding = 'lsb'

    _lead_in = [TIMING, -TIMING * 5]
    _lead_out = [-15000]
    _middle_timings = []
    _bursts = [[-TIMING, TIMING], [TIMING, -TIMING]]

    _has_repeat_lead_out = True

    _code_order = [
        ['F', 8],
        ['D', 7]
    ]

    _parameters = [
        ['C0', 0, 0],
        ['F', 1, 8],
        ['D', 9, 15]
    ]
    # [D:0..127,F:0..255]
    encode_parameters = [
        ['device', 0, 127],
        ['function', 0, 255],
    ]

    def decode(self, data, frequency=0):
        try:
            code = protocol_base.IrProtocolBase.decode(self, data, frequency)
        except DecodeError:
            if self._lead_out == [-110000]:
                self._lead_out = [-15000]
                code = protocol_base.IrProtocolBase.decode(self, data, frequency)
            else:
                self._lead_out = [-110000]
                code = protocol_base.IrProtocolBase.decode(self, data, frequency)

        if self._lead_out == [-15000]:
            if self._last_code is None:
                if code.c0 != 1 or code.device != 127 and code.function != 254:
                    raise DecodeError('Invalid checksum')

                raise RepeatLeadIn

            if self._last_code == code:
                return self._last_code

            raise RepeatLeadOut('Invalid repeat frame')

        if self._last_code is not None:
            if self._last_code == code:
                return self._last_code

            self._last_code.repeat_timer.stop()
            self._last_code = None
            raise RepeatLeadOut('Invalid frame')

        self._last_code = code
        return code

    def encode(self, device, function, repeat_count=0):
        lead_out = self._lead_out

        self._lead_out = [-15000]

        c0 = 1
        f = 254
        d = 127

        prefix = self._build_packet(
            list(self._get_timing(c0, i) for i in range(1)),
            list(self._get_timing(f, i) for i in range(8)),
            list(self._get_timing(d, i) for i in range(7))
        )

        suffix = self._build_packet(
            list(self._get_timing(c0, i) for i in range(1)),
            list(self._get_timing(f, i) for i in range(8)),
            list(self._get_timing(d, i) for i in range(7))
        )

        self._lead_out = [-110000]

        code = self._build_packet(
            list(self._get_timing(c0, i) for i in range(1)),
            list(self._get_timing(function, i) for i in range(8)),
            list(self._get_timing(device, i) for i in range(7))
        )

        self._lead_out = lead_out

        packet = [prefix]
        packet += [code] * (repeat_count + 1)
        packet += [suffix]

        params = dict(
            frequency=self.frequency,
            D=device,
            F=function,
        )

        code = protocol_base.IRCode(
            self,
            [prefix[:], code[:], suffix[:]],
            packet[:],
            params,
            repeat_count
        )

        return code

    def _test_decode(self):
        rlc_codes = [
            [
                +500, -2500, +500, -1000, +1000, -500, +500, -500, +500, -500, +500, -500, +500, -500, +500, -500,
                +500, -500, +500, -500, +500, -500, +500, -500, +500, -500, +500, -500, +500, -500, +500, -15500
            ],
            [
                +500, -2500, +500, -1000, +1000, -1000, +1000, -500, +500, -500, +500, -500, +500, -1000,
                +1000, -500, +500, -500, +500, -500, +500, -1000, +500, -500, +500, -500, +500, -110000
            ],
            [
                +500, -2500, +500, -1000, +1000, -500, +500, -500, +500, -500, +500, -500, +500, -500, +500, -500,
                +500, -500, +500, -500, +500, -500, +500, -500, +500, -500, +500, -500, +500, -500, +500, -15500
            ]
        ]

        params = [
            dict(device=127, function=254),
            dict(device=15, function=122),
            dict(device=127, function=254),
        ]

        return protocol_base.IrProtocolBase._test_decode(self, rlc_codes, params)

    def _test_encode(self):
        params = dict(device=15, function=122)
        protocol_base.IrProtocolBase._test_encode(self, params)


NRC16 = NRC16()
