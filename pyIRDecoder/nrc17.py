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

    _repeat_lead_in = []
    _repeat_lead_out = []
    _repeat_bursts = []

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

    repeat_timeout = 130500

    def reset(self):
        self._lead_out = [-TIMING * 28]
        self._last_code = None

    def _calc_checksum(self, device, sub_device):
        c = 0
        for i in range(4):
            c = self._set_bit(c, i, self._get_bit(device, 1))
            c = self._set_bit(c, i + 4, self._get_bit(sub_device, i))

        return c

    def decode(self, data, frequency=0):
        try:
            code = protocol_base.IrProtocolBase.decode(self, data, frequency)
        except DecodeError:
            self._lead_out = [-TIMING * 200]
            try:
                code = protocol_base.IrProtocolBase.decode(self, data, frequency)
            except DecodeError:
                self.reset()
                raise

        if code.c0 != 1:
            self.reset()
            raise DecodeError('Invalid checksum')

        checksum = self._calc_checksum(code.device, code.sub_device)

        if self._lead_out[0] in (-TIMING * 200, -TIMING * 28):
            if code.function != 0xFE or checksum != 0xFF:
                self._last_code = None
                raise DecodeError('Invalid repeat lead out')

        if self._lead_out[0] == -TIMING * 200:
            if self._last_code is not None:
                self._last_code.repeat_timer.stop()

            self.reset()
            raise RepeatLeadOut

        if self._lead_out[0] == -TIMING * 28:
            self._lead_out = [-TIMING * 220]
            raise RepeatLeadIn

        if self._last_code is None:
            self._last_code = code

        elif not self._last_code.repeat_timer.is_running:
            raise RepeatTimeoutExpired

        if self._last_code != code:
            raise DecodeError('Repeat code does not match last code')

        # self._last_code.repeat_timer.start()
        return self._last_code

    def encode(self, device, sub_device, function):
        lead_out = self._lead_out

        c0 = 1
        f = 254
        d = 15
        s = 15

        self._lead_out = [-TIMING * 28]
        prefix = self._build_packet(
            list(self._get_timing(c0, i) for i in range(1)),
            list(self._get_timing(f, i) for i in range(8)),
            list(self._get_timing(d, i) for i in range(4)),
            list(self._get_timing(s, i) for i in range(4))
        )

        self._lead_out = [-TIMING * 200]
        suffix = self._build_packet(
            list(self._get_timing(c0, i) for i in range(1)),
            list(self._get_timing(f, i) for i in range(8)),
            list(self._get_timing(d, i) for i in range(4)),
            list(self._get_timing(s, i) for i in range(4))
        )

        self._lead_out = [-TIMING * 220]
        code = self._build_packet(
            list(self._get_timing(c0, i) for i in range(1)),
            list(self._get_timing(function, i) for i in range(8)),
            list(self._get_timing(device, i) for i in range(4)),
            list(self._get_timing(sub_device, i) for i in range(4))
        )

        self._lead_out = lead_out

        return [prefix, code, suffix]

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

        protocol_base.IrProtocolBase._test_decode(self, rlc_codes, params)

    def _test_encode(self):
        params = dict(device=14, function=140)
        protocol_base.IrProtocolBase._test_encode(self, params)


NRC17 = NRC17()
