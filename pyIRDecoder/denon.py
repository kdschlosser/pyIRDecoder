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

TIMING = 264


class Denon(protocol_base.IrProtocolBase):
    """
    IR decoder for the Denon protocol.
    """
    irp = '{38k,264,lsb}<1,-3|1,-7>(D:5,F:8,0:2,1,-165,D:5,~F:8,3:2,1,-165)*'
    frequency = 38000
    bit_count = 30
    encoding = 'lsb'

    _lead_out = [TIMING, -TIMING * 165]
    _middle_timings = [(TIMING, -TIMING * 165)]
    _bursts = [[TIMING, -TIMING * 3], [TIMING, -TIMING * 7]]

    _code_order = [
        ['D', 5],
        ['F', 8]
    ]

    _parameters = [
        ['D', 0, 4],
        ['F', 5, 12],
        ['C0', 13, 14],
        ['D_CHECKSUM', 15, 19],
        ['F_CHECKSUM', 20, 27],
        ['C1', 28, 29]
    ]
    # [D:0..31,F:0..255]
    encode_parameters = [
        ['device', 0, 31],
        ['function', 0, 255],
    ]

    def _calc_checksum(self, function):
        f = self._invert_bits(function, 8)
        return f

    def decode(self, data, frequency=0):
        try:
            c = protocol_base.code_wrapper.CodeWrapper(
                self.encoding,
                self._lead_in[:],
                self._lead_out[:],
                self._middle_timings[:],
                self._bursts[:],
                self.tolerance,
                data[:]
            )

            if c.num_bits > self.bit_count:
                raise DecodeError('To many bits')
            elif c.num_bits < self.bit_count:
                raise DecodeError('Not enough bits')

            params = dict(frequency=self.frequency)
            for name, start, stop in self._parameters:
                params[name] = c.get_value(start, stop)

            code = protocol_base.IRCode(self, c.original_code, list(c), params)
            code._code = c

            code = protocol_base.IrProtocolBase.decode(self, data, frequency)
        except DecodeError:
            c = protocol_base.code_wrapper.CodeWrapper(
                self.encoding,
                self._lead_in[:],
                self._lead_out[:],
                [],
                self._bursts[:],
                self.tolerance,
                data[:]
            )

            if c.num_bits > self.bit_count // 2:
                raise DecodeError('To many bits')
            elif c.num_bits < self.bit_count // 2:
                raise DecodeError('Not enough bits')

            params = dict(frequency=self.frequency)
            for name, start, stop in self._parameters[:3]:
                params[name] = c.get_value(start, stop)

            code = protocol_base.IRCode(self, c.original_code, list(c), params)
            code._code = c

            if len(self._sequence) == 0:
                self._sequence.append(code)
                raise RepeatLeadIn

            c = self._sequence[0]

            params = dict(
                frequency=self.frequency,
                D=c.device,
                F=c.function,
                C0=c.C0,
                D_CHECKSUM=code.device,
                F_CHECKSUM=code.function,
                C1=code.c0
            )

            code = protocol_base.IRCode(
                self,
                c.original_rlc + code.original_rlc,
                c.normalized_rlc + code.normalized_rlc,
                params
            )
            del self._sequence[:]

        if self._last_code is not None:
            if self._last_code == code:
                return self._last_code

            self._last_code.repeat_timer.stop()
            self._last_code = None

        if code.c0 != 0 or code.c1 != 3:
            raise DecodeError('invalid checksum')

        func_checksum = self._calc_checksum(code.function)

        if code.device != code.d_checksum or func_checksum != code.f_checksum:
            raise DecodeError('Invalid checksum')

        self._last_code = code
        return code

    def encode(self, device, function, repeat_count=0):
        c0 = 0
        c1 = 3
        func_checksum = self._calc_checksum(function)

        packet1 = self._build_packet(
            list(self._get_timing(device, i) for i in range(5)),
            list(self._get_timing(function, i) for i in range(8)),
            list(self._get_timing(c0, i) for i in range(2))
        )
        packet2 = self._build_packet(
            list(self._get_timing(device, i) for i in range(5)),
            list(self._get_timing(func_checksum, i) for i in range(8)),
            list(self._get_timing(c1, i) for i in range(2)),
        )

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
                +264, -1848, +264, -792, +264, -1848, +264, -1848, +264, -1848, +264, -1848, +264, -1848, +264, -1848,
                +264, -792, +264, -792, +264, -1848, +264, -1848, +264, -1848, +264, -792, +264, -792, +264, -43560
            ],
            [
                +264, -1848, +264, -792, +264, -1848, +264, -1848, +264, -1848, +264, -792, +264, -792, +264, -792,
                +264, -1848, +264, -1848, +264, -792, +264, -792, +264, -792, +264, -1848, +264, -1848, +264, -43560
            ]
        ]

        params = [dict(device=26, function=238)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(device=26, function=238)
        protocol_base.IrProtocolBase._test_encode(self, params)


Denon = Denon()

