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


class F121(protocol_base.IrProtocolBase):
    """
    IR decoder for the F121 protocol.
    """

    irp = '{37.9k,422,lsb}<1,-3|3,-1>(D:3,H:1,F:8,-34,D:3,H:1,F:8){H=0}'


    irp = '{37.9k,422,lsb}<1,-3|3,-1>(D:3,H:1,F:8,-34,D:3,H:1,F:8,-88,D:3,H:1,F:8,-34,D:3,H:1,F:8)*{H=1}'
    frequency = 37900
    bit_count = 48
    encoding = 'lsb'

    _lead_in = []
    _lead_out = []
    _middle_timings = [-TIMING * 34, -TIMING * 88, -TIMING * 34]
    _bursts = [[TIMING, -TIMING * 3], [TIMING * 3, -TIMING]]

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
        ['F1', 16, 23],
        ['D2', 24, 26],
        ['H2', 27, 27],
        ['F2', 28, 35],
        ['D3', 36, 38],
        ['H3', 39, 39],
        ['F3', 40, 47]
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

            if c.num_bits > self.bit_count / 4:
                raise DecodeError('To many bits')
            elif c.num_bits < self.bit_count / 4:
                raise DecodeError('Not enough bits')

            prms = dict(frequency=self.frequency)
            for name, start, stop in self._parameters[:3]:
                prms[name] = c.get_value(start, stop)

            c = protocol_base.IRCode(self, c.original_code, list(c), prms)
            if c.h != 1:
                raise DecodeError('Invalid checksum')

            return c

        try:
            code = protocol_base.IrProtocolBase.decode(self, data, frequency)
        except DecodeError:
            try:
                if len(self._sequence) == 0:
                    self._sequence.append(_get_code([self._middle_timings[0]]))
                    raise RepeatLeadIn
                if len(self._sequence) == 1:
                    self._sequence.append(_get_code([self._middle_timings[1]]))
                    raise RepeatLeadIn
                if len(self._sequence) == 2:
                    self._sequence.append(_get_code([self._middle_timings[2]]))
                    raise RepeatLeadIn

                self._sequence.append(_get_code([]))

                params = dict(
                    frequency=self.frequency
                )
                normalized_rlc = []
                original_rlc = []

                for i, code in enumerate(self._sequence):
                    if i == 0:
                        num = ''
                    else:
                        num = str(i)

                    params['D' + num] = code.device
                    params['F' + num] = code.function
                    params['H' + num] = code.h
                    normalized_rlc += code.normalized_rlc[0]
                    original_rlc += code.original_rlc[0]

                code = protocol_base.IRCode(self, original_rlc, normalized_rlc, params)
            except DecodeError:
                del self._sequence[:]
                raise

        if self._last_code is not None:
            if self._last_code == code:
                return self._last_code

            self._last_code.repeat_timer.stop()
            self._last_code = None

        if (
            code.device != code.d1 != code.d2 != code.d3 or
            code.h != code.h1 != 1 != code.h2 != code.h3 or
            code.function != code.f1 != code.f2 != code.f3
        ):
            raise DecodeError('Invalid checksum')

        self._last_code = code
        return code

    def encode(self, device, function, repeat_count=0):
        h = 1

        packet1 = self._build_packet(
            list(self._get_timing(device, i) for i in range(3)),
            list(self._get_timing(h, i) for i in range(1)),
            list(self._get_timing(function, i) for i in range(8))
        )

        packet2 = packet1[:]
        packet3 = packet1[:]
        packet4 = packet1[:]

        packet1[-1] += self._middle_timings[0]
        packet2[-1] += self._middle_timings[1]
        packet3[-1] += self._middle_timings[2]

        packet = [packet1, packet2, packet3, packet4]

        params = dict(
            frequency=self.frequency,
            D=device,
            F=function,
        )

        code = protocol_base.IRCode(
            self,
            packet[:],
            packet[:] * (repeat_count + 1),
            params,
            repeat_count
        )
        return code

    def _test_decode(self):
        rlc = [
            [
                422, -1266, 1266, -422, 1266, -422, 1266, -422, 1266, -422, 422, -1266, 1266, -422, 422, -1266,
                422, -1266, 422, -1266, 1266, -422, 422, -15614
            ],
            [
                422, -1266, 1266, -422, 1266, -422, 1266, -422, 1266, -422, 422, -1266, 1266, -422, 422, -1266, 422,
                -1266, 422, -1266, 1266, -422, 422, -38402
            ],
            [
                422, -1266, 1266, -422, 1266, -422, 1266, -422, 1266, -422, 422, -1266, 1266, -422, 422, -1266,
                422, -1266, 422, -1266, 1266, -422, 422, -15614
            ],
            [
                422, -1266, 1266, -422, 1266, -422, 1266, -422, 1266, -422, 422, -1266, 1266, -422, 422, -1266, 422,
                -1266, 422, -1266, 1266, -422, 422, -1266
            ]
        ]

        params = [
            None,
            None,
            None,
            dict(device=6, function=69)
        ]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(device=6, function=69)
        protocol_base.IrProtocolBase._test_encode(self, params)


F121 = F121()
