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


TIMING = 560


class Sunfire(protocol_base.IrProtocolBase):
    """
    IR decoder for the Sunfire protocol.
    """
    irp = '{38k,560,msb}<1,-1|3,-1>(16,-8, D:4,F:8,~D:4,~F:8,-32)*'
    frequency = 38000
    bit_count = 24
    encoding = 'msb'

    _lead_in = [TIMING * 16, -TIMING * 8]
    _lead_out = [-TIMING * 32]
    _middle_timings = []
    _bursts = [[TIMING, -TIMING], [TIMING * 3, -TIMING]]

    _code_order = [
        ['D', 4],
        ['F', 8],
    ]

    _parameters = [
        ['D', 0, 3],
        ['F', 4, 11],
        ['D_CHECKSUM', 12, 15],
        ['F_CHECKSUM', 16, 23],
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
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)
        if self._last_code is not None:
            if self._last_code == code:
                return self._last_code

            self._last_code.repeat_timer.stop()
            self._last_code = None

        dev_checksum, func_checksum = self._calc_checksum(code.device, code.function)

        if dev_checksum != code.d_checksum or func_checksum != code.f_checksum:
            raise DecodeError('Checksum failed')

        self._last_code = code
        return code

    def encode(self, device, function, repeat_count=0):
        dev_checksum, func_checksum = self._calc_checksum(device, function)

        packet = self._build_packet(
            list(self._get_timing(device, i) for i in range(4)),
            list(self._get_timing(function, i) for i in range(8)),
            list(self._get_timing(dev_checksum, i) for i in range(4)),
            list(self._get_timing(func_checksum, i) for i in range(8)),
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
        rlc = [
            [
                +8960, -4480, +1680, -560, +1680, -560, +1680, -560, +560, -560, +560, -560, +1680, -560, +1680, -560,
                +1680, -560, +1680, -560, +1680, -560, +560, -560, +560, -560, +560, -560, +560, -560, +560, -560,
                +1680, -560, +1680, -560, +560, -560, +560, -560, +560, -560, +560, -560, +560, -560, +1680, -560,
                +1680, -18480
            ]
        ]

        params = [dict(function=124, device=14)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(function=124, device=14)
        protocol_base.IrProtocolBase._test_encode(self, params)


Sunfire = Sunfire()
