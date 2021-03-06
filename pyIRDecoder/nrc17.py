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


class NRC17(protocol_base.IrProtocolBase):
    """
    IR decoder for the NRC17 protocol.
    """
    irp = '{38k,500,lsb}<-1,1|1,-1>(1,-5,1:1,254:8,255:8,-28,(1,-5,1:1,F:8,D:4,S:4,-220)*,1,-5,1:1,254:8,255:8,-200)'
    frequency = 38000
    bit_count = 17
    encoding = 'lsb'

    _lead_in = [TIMING, -TIMING * 5]
    _lead_out = [-TIMING * 28]
    _middle_timings = []
    _bursts = [[-TIMING, TIMING], [TIMING, -TIMING]]

    _has_repeat_lead_out = True

    _code_order = [
        ['F', 8],
        ['D', 4],
        ['S', 4],
    ]

    _parameters = [
        ['C0', 0, 0],
        ['F', 1, 8],
        ['D', 9, 12],
        ['S', 13, 16]

    ]
    # [D:0..15,S:0..15,F:0..255]
    encode_parameters = [
        ['device', 0, 15],
        ['sub_device', 0, 15],
        ['function', 0, 255],
    ]

    def _calc_checksum(self, device, sub_device):
        c = 0
        for i in range(4):
            c = self._set_bit(c, i, self._get_bit(device, 1))
            c = self._set_bit(c, i + 4, self._get_bit(sub_device, i))

        return c

    def decode(self, data, frequency=0):
        lead_outs = [-TIMING * 28, -TIMING * 220, -TIMING * 200]
        for lead_out in lead_outs:
            self._lead_out[0] = lead_out
            try:
                code = protocol_base.IrProtocolBase.decode(self, data, frequency)
                break
            except DecodeError:
                continue
        else:
            raise

        if code.c0 != 1:
            raise DecodeError('Invalid checksum')

        checksum = self._calc_checksum(code.device, code.sub_device)

        if self._lead_out[0] == -TIMING * 28:
            if code.function != 0xFE or checksum != 0xFF:
                raise DecodeError('Invalid lead in')

            raise RepeatLeadIn

        if self._lead_out[0] == -TIMING * 200:
            if code.function != 0xFE or checksum != 0xFF:
                raise DecodeError('Invalid lead out')

            if self._last_code is not None:
                self._last_code.repeat_timer.stop()
                self._last_code = None

            raise RepeatLeadOut

        if self._last_code is not None:
            if self._last_code == code:
                return self._last_code

            self._last_code.repeat_timer.stop()
            self._last_code = None
            raise RepeatLeadOut

        self._last_code = code
        return code

    def encode(self, device, sub_device, function, repeat_count=0):
        lead_out = self._lead_out

        c0 = 1
        f = 254
        d = 15
        s = 15

        self._lead_out[0] = -TIMING * 28
        prefix = self._build_packet(
            list(self._get_timing(c0, i) for i in range(1)),
            list(self._get_timing(f, i) for i in range(8)),
            list(self._get_timing(d, i) for i in range(4)),
            list(self._get_timing(s, i) for i in range(4))
        )

        self._lead_out[0] = -TIMING * 200
        suffix = self._build_packet(
            list(self._get_timing(c0, i) for i in range(1)),
            list(self._get_timing(f, i) for i in range(8)),
            list(self._get_timing(d, i) for i in range(4)),
            list(self._get_timing(s, i) for i in range(4))
        )

        self._lead_out[0] = -TIMING * 220
        code = self._build_packet(
            list(self._get_timing(c0, i) for i in range(1)),
            list(self._get_timing(function, i) for i in range(8)),
            list(self._get_timing(device, i) for i in range(4)),
            list(self._get_timing(sub_device, i) for i in range(4))
        )

        self._lead_out = lead_out

        packet = [prefix]
        packet += [code] * (repeat_count + 1)
        packet += [suffix]

        params = dict(
            frequency=self.frequency,
            D=device,
            S=sub_device,
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
                500, -2500, 500, -1000, 1000, -500, 500, -500, 500, -500, 500, -500, 500, -500, 500, -500, 500, -500,
                500, -500, 500, -500, 500, -500, 500, -500, 500, -500, 500, -500, 500, -500, 500, -14500
            ],
            [
                500, -2500, 500, -1000, 1000, -1000, 500, -500, 1000, -500, 500, -500, 500, -1000, 500, -500,
                1000, -500, 500, -500, 500, -500, 500, -500, 500, -1000, 500, -500, 500, -110000
            ],
            [
                500, -2500, 500, -1000, 1000, -500, 500, -500, 500, -500, 500, -500, 500, -500, 500, -500, 500, -500,
                500, -500, 500, -500, 500, -500, 500, -500, 500, -500, 500, -500, 500, -500, 500, -100500
            ]
        ]

        params = [
            None,
            dict(device=14, sub_device=3, function=114),
            None,
        ]

        return protocol_base.IrProtocolBase._test_decode(self, rlc_codes, params)

    def _test_encode(self):
        params = dict(device=14, function=140)
        protocol_base.IrProtocolBase._test_encode(self, params)


NRC17 = NRC17()
