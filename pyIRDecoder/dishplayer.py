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


TIMING = 535


class DishPlayer(protocol_base.IrProtocolBase):
    """
    IR decoder for the DishPlayer protocol.
    """
    irp = '{38.4k,535,msb}<1,-5|1,-3>(1,-11,(F:6,S:5,D:2,1,-11)+)'
    frequency = 38400
    bit_count = 13
    encoding = 'msb'

    _lead_in = [TIMING, -TIMING * 11]
    _lead_out = [TIMING, -TIMING * 11]
    _bursts = [[TIMING, -TIMING * 5], [TIMING, -TIMING * 3]]

    _code_order = [
        ['F', 6],
        ['S', 5],
        ['D', 2]
    ]

    _parameters = [
        ['F', 0, 5],
        ['S', 6, 10],
        ['D', 11, 12],
    ]
    # [F:0..63,S:0..31,D:0..3]
    encode_parameters = [
        ['device', 0, 3],
        ['sub_device', 0, 31],
        ['function', 0, 63]
    ]

    def decode(self, data, frequency=0):
        self._lead_in = [TIMING, -TIMING * 11]

        try:
            code = protocol_base.IrProtocolBase.decode(self, data, frequency)
        except DecodeError:
            if self._last_code is None and len(self._sequence) == 0:
                raise

            del self._lead_in[:]
            code = protocol_base.IrProtocolBase.decode(self, data, frequency)

        if self._lead_in:
            if self._last_code is not None:
                self._last_code.repeat_timer.stop()
                self._last_code = None

            self._sequence.append(code)
            raise RepeatLeadIn

        if self._last_code is not None:
            if self._last_code == code:
                return self._last_code

            raise DecodeError('invalid repeat frame')

        tt = sum(abs(item) for item in code.normalized_rlc[0])

        original_rlc = [self._sequence[0].original_rlc[0], code.original_rlc[0]]
        normalized_rlc = [self._sequence[0].normalized_rlc[0], code.normalized_rlc[0]]

        params = dict(
            D=code.device,
            S=code.sub_device,
            F=code.function,
            frequency=self.frequency
        )

        self.repeat_timeout = tt
        code = protocol_base.IRCode(
            self,
            original_rlc,
            normalized_rlc,
            params
        )

        self.repeat_timeout = 0
        del self._sequence[:]
        self._last_code = code
        return code

    def encode(self, device, sub_device, function, repeat_count=0):
        lead_in = self._lead_in[:]

        self._lead_in = [TIMING, -TIMING * 11]
        packet = self._build_packet(
            list(self._get_timing(function, i) for i in range(6)),
            list(self._get_timing(sub_device, i) for i in range(5)),
            list(self._get_timing(device, i) for i in range(2)),
        )
        del self._lead_in[:]
        repeat = self._build_packet(
            list(self._get_timing(function, i) for i in range(6)),
            list(self._get_timing(sub_device, i) for i in range(5)),
            list(self._get_timing(device, i) for i in range(2)),
        )

        self._lead_in = lead_in[:]

        params = dict(
            frequency=self.frequency,
            D=device,
            S=sub_device,
            F=function,
        )

        code = protocol_base.IRCode(
            self,
            [packet[:], repeat[:]],
            [packet[:]] + ([repeat] * (repeat_count + 1)),
            params,
            repeat_count
        )
        return code

    def _test_decode(self):
        rlc = [
            [
                +535, -5885, +535, -2675, +535, -2675, +535, -2675, +535, -1605, +535, -2675, +535, -1605, +535, -2675,
                +535, -2675, +535, -2675, +535, -2675, +535, -1605, +535, -2675, +535, -2675, +535, -5885
            ],
            [
                +535, -2675, +535, -2675, +535, -2675, +535, -1605, +535, -2675, +535, -1605, +535, -2675, +535, -2675,
                +535, -2675, +535, -2675, +535, -1605, +535, -2675, +535, -2675, +535, -5885
            ]

        ]

        params = [dict(device=0, function=5, sub_device=1), dict(device=0, function=5, sub_device=1)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(device=0, function=5, sub_device=1)
        protocol_base.IrProtocolBase._test_encode(self, params)


DishPlayer = DishPlayer()
