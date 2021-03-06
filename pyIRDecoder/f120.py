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

TIMING = 422


class F120(protocol_base.IrProtocolBase):
    """
    IR decoder for the F120 protocol.
    """
    irp = '{37.9k,422,lsb}<1,-3|3,-1>(D:3,H:1,F:8,-34,D:3,H:1,F:8){H=0}'
    frequency = 37900
    bit_count = 24
    encoding = 'lsb'

    _lead_in = []
    _lead_out = []
    _middle_timings = [-TIMING * 34]
    _bursts = [[TIMING, -TIMING * 3], [TIMING * 3, -TIMING]]

    _repeat_lead_in = []
    _repeat_lead_out = []
    _repeat_bursts = []

    _code_order = [
        ['D', 3],
        ['F', 8],
    ]

    _parameters = [
        ['D', 0, 2],
        ['H', 3, 3],
        ['F', 4, 11],
        ['D1', 12, 14],
        ['H1', 15, 15],
        ['F1', 16, 23]
    ]
    # [D:0..7,F:0..255]
    encode_parameters = [
        ['device', 0, 7],
        ['function', 0, 255]
    ]

    def decode(self, data, frequency=0):
        def _get_code(lead_out):
            c = protocol_base.code_wrapper.CodeWrapper(
                self.encoding,
                self._lead_in[:],
                lead_out,
                [],
                self._bursts[:],
                self.tolerance,
                data[:]
            )

            if c.num_bits > self.bit_count / 2:
                raise DecodeError('To many bits')
            elif c.num_bits < self.bit_count / 2:
                raise DecodeError('Not enough bits')

            prms = dict(frequency=self.frequency)
            for name, start, stop in self._parameters[:3]:
                prms[name] = c.get_value(start, stop)

            c = protocol_base.IRCode(self, c.original_code, list(c), prms)
            if c.h != 0:
                raise DecodeError('Invalid checksum')

            return c

        try:
            code = protocol_base.IrProtocolBase.decode(self, data, frequency)
        except DecodeError:
            if len(self._sequence) == 0:
                self._sequence.append(_get_code(self._middle_timings))
                raise RepeatLeadIn
            else:
                try:
                    code = _get_code([])
                except DecodeError:
                    del self._sequence[:]
                    raise

                original_rlc = self._sequence[0].original_rlc[0] + code.original_rlc[0]
                normalized_rlc = self._sequence[0].normalized_rlc[0] + code.normalized_rlc[0]
                params = dict(
                    D=self._sequence[0].device,
                    F=self._sequence[0].function,
                    H=self._sequence[0].h,
                    D1=code.device,
                    F1=code.function,
                    H1=code.h,
                    frequency=self.frequency
                )

                code = protocol_base.IRCode(
                    self,
                    original_rlc,
                    normalized_rlc,
                    params
                )

                del self._sequence[:]

        if self._last_code is not None:
            if self._last_code == code:
                return self._last_code

            self._last_code.repeat_timer.stop()

        if (
            code.device != code.d1 or
            code.h != 0 != code.h1 or
            code.function != code.f1
        ):
            raise DecodeError('Invalid checksum')

        self._last_code = code
        return code

    def encode(self, device, function, repeat_count=0):
        h = 0

        packet1 = self._build_packet(
            list(self._get_timing(device, i) for i in range(3)),
            list(self._get_timing(h, i) for i in range(1)),
            list(self._get_timing(function, i) for i in range(8)),
        )
        packet2 = packet1[:]

        packet1[-1] += self._middle_timings[0]

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
                +1266, -422, +422, -1266, +1266, -422, +422, -1266, +422, -1266, +422, -1266, +422, -1266, +1266, -422,
                +1266, -422, +1266, -422, +422, -1266, +422, -15614
            ],
            [
                +1266, -422, +422, -1266, +1266, -422, +422, -1266, +422, -1266, +422, -1266, +422, -1266, +1266, -422,
                +1266, -422, +1266, -422, +422, -1266, +422, -1266
            ]
        ]

        params = [
            None,
            dict(device=5, function=56)
        ]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(device=5, function=56)
        protocol_base.IrProtocolBase._test_encode(self, params)


F120 = F120()
