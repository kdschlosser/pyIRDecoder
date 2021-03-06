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
from . import DecodeError, RepeatLeadIn


TIMING = 460


class RCAOld(protocol_base.IrProtocolBase):
    """
    IR decoder for the RCAOld protocol.
    """
    irp = '{58k,460,msb}<1,-2|1,-4>([40][8],-8,D:4,F:8,~D:4,~F:8,2,-16)'
    frequency = 58000
    bit_count = 24
    encoding = 'msb'

    _lead_in = [TIMING * 40, -TIMING * 8]
    _lead_out = [TIMING * 2, -TIMING * 16]
    _middle_timings = []
    _bursts = [[TIMING, -TIMING * 2], [TIMING, -TIMING * 4]]

    _code_order = [
        ['D', 4],
        ['F', 8],
    ]

    _parameters = [
        ['D', 0, 3],
        ['F', 4, 11],
        ['D_CHECKSUM', 12, 15],
        ['F_CHECKSUM', 16, 23]
    ]
    # [D:0..15,F:0..255]
    encode_parameters = [
        ['device', 0, 15],
        ['function', 0, 255],
    ]

    def _calc_checksum(self, device, function):
        d = self._invert_bits(device, 4)
        f = self._invert_bits(function, 8)
        return d, f

    def decode(self, data, frequency=0):
        try:
            code = protocol_base.IrProtocolBase.decode(self, data, frequency)
        except DecodeError:
            if self._lead_in[0] == TIMING * 8:
                self._lead_in[0] = TIMING * 40
            else:
                self._lead_in[0] = TIMING * 8

            code = protocol_base.IrProtocolBase.decode(self, data, frequency)

        d_checksum, f_checksum = self._calc_checksum(code.device, code.function)

        if f_checksum != code.f_checksum or d_checksum != code.d_checksum:
            raise DecodeError('Checksum failed')

        if len(self._sequence) == 0:
            if self._lead_in[0] != TIMING * 40:
                raise DecodeError('Invalid frame')

            self._sequence.append(code)
            raise RepeatLeadIn

        if self._lead_in[0] != TIMING * 8:
            del self._sequence[:]
            raise DecodeError('Invalid frame')

        if self._last_code is not None:
            if self._last_code == code:
                return self._last_code

            self._last_code.repeat_timer.stop()
            self._last_code = None

        self._last_code = code
        return code

    def encode(self, device, function, repeat_count=0):
        d_checksum, f_checksum = self._calc_checksum(
            device,
            function,
        )

        lead_in = self._lead_in[0]

        self._lead_in[0] = TIMING * 40

        packet1 = self._build_packet(
            list(self._get_timing(device, i) for i in range(4)),
            list(self._get_timing(function, i) for i in range(8)),
            list(self._get_timing(d_checksum, i) for i in range(4)),
            list(self._get_timing(f_checksum, i) for i in range(8))
        )

        self._lead_in[0] = TIMING * 8

        packet2 = self._build_packet(
            list(self._get_timing(device, i) for i in range(4)),
            list(self._get_timing(function, i) for i in range(8)),
            list(self._get_timing(d_checksum, i) for i in range(4)),
            list(self._get_timing(f_checksum, i) for i in range(8))
        )

        self._lead_in[0] = lead_in

        params = dict(
            frequency=self.frequency,
            D=device,
            F=function,
        )

        code = protocol_base.IRCode(
            self,
            [packet1[:], packet2[:]],
            [packet1[:], packet2[:]] * (repeat_count + 1),
            params,
            repeat_count
        )

        return code

    def _test_decode(self):
        rlc = [
            [
                18400, -3680, 460, -1840, 460, -920, 460, -1840, 460, -1840, 460, -1840, 460, -920, 460, -1840,
                460, -920, 460, -1840, 460, -920, 460, -920, 460, -1840, 460, -920, 460, -1840, 460, -920,
                460, -920, 460, -920, 460, -1840, 460, -920, 460, -1840, 460, -920, 460, -1840, 460, -1840,
                460, -920, 920, -7360
            ],
            [
                3680, -3680, 460, -1840, 460, -920, 460, -1840, 460, -1840, 460, -1840, 460, -920, 460, -1840,
                460, -920, 460, -1840, 460, -920, 460, -920, 460, -1840, 460, -920, 460, -1840, 460, -920,
                460, -920, 460, -920, 460, -1840, 460, -920, 460, -1840, 460, -920, 460, -1840, 460, -1840,
                460, -920, 920, -7360
            ]
        ]

        params = [dict(device=11, function=169), None]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(device=11, function=169)
        protocol_base.IrProtocolBase._test_encode(self, params)


RCAOld = RCAOld()
