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


TIMING = 780


class Dyson(protocol_base.IrProtocolBase):
    """
    IR decoder for the Dyson protocol.
    """
    irp = '{38k,780,lsb}<1,-1|1,-2>(3,-1,D:7,F:6,T:-2,1,-100m,3,-1,D:7,F:6,T:-2,1,-60m,(3,-1,1:1,1,-60m)*)'
    frequency = 38000
    bit_count = 30
    encoding = 'lsb'

    _lead_in = [TIMING * 3, -TIMING]
    _lead_out = [TIMING, -60000]
    _middle_timings = [(TIMING, -100000), (TIMING * 3, -TIMING)]
    _bursts = [[TIMING, -TIMING], [TIMING, -TIMING * 2]]

    _backup_middle_timings = _middle_timings[:]

    _repeat_lead_in = [TIMING * 3, -TIMING]
    _repeat_lead_out = [TIMING, -60000]
    _repeat_bursts = [[TIMING, -TIMING], [TIMING, -TIMING * 3]]

    repeat_timeout = (TIMING * 9) + 70000

    _code_order = [
        ['D', 7],
        ['F', 6]
    ]

    _parameters = [
        ['D', 0, 6],
        ['F', 7, 12],
        ['T', 13, 14],
        ['D2', 15, 21],
        ['F2', 22, 27],
        ['T2', 28, 29]
    ]
    # [D:0..127,F:0..63,T:0..3=0]
    encode_parameters = [
        ['device', 0, 127],
        ['function', 0, 63],
        ['toggle', 0, 3]
    ]

    def decode(self, data, frequency=0):
        if len(self._sequence) == 1:
            self._lead_out[1] = -60000
            del self._middle_timings[:]

        elif self._last_code is None:
            self._lead_out[1] = -60000
            self._middle_timings = self._backup_middle_timings[:]

        try:
            code = protocol_base.IrProtocolBase.decode(self, data, frequency)
        except DecodeError:
            if len(self._sequence) == 0:
                self._lead_out = list(self._backup_middle_timings[0])
                del self._middle_timings[:]
                code = protocol_base.IrProtocolBase.decode(self, data, frequency)
            else:
                raise

        if self._last_code is not None:
            if self._last_code == code:
                return self._last_code

            self._last_code.repeat_timer.stop()
            self._last_code = None

        if self._middle_timings:
            self._last_code = code
            return code

        if len(self._sequence) == 1:
            original_rlc = self._sequence[0].original_rlc[0] + code.original_rlc[0]
            normalized_rlc = self._sequence[0].normalized_rlc[0] + code.normalized_rlc[0]
            params = dict(
                D=self._sequence[0].device,
                F=self._sequence[0].function,
                T=self._sequence[0].toggle,
                D1=code.device,
                F1=code.function,
                T1=code.toggle,
                frequency=self.frequency
            )

            code = protocol_base.IRCode(
                self,
                original_rlc,
                normalized_rlc,
                params
            )

            del self._sequence[:]

            if code.device != code.d2 or code.function != code.f2:
                raise DecodeError('Checksum failed')

            self._last_code = code
            return code

        self._sequence.append(code)
        raise RepeatLeadIn

    def encode(self, device, function, toggle, repeat_count=0):
        # toggle = self._reverse_bits(toggle, 2)

        packet = [
            self._build_packet(
                list(self._get_timing(device, i) for i in range(7)),
                list(self._get_timing(function, i) for i in range(6)),
                list(self._get_timing(toggle, i) for i in range(2)),
                self._middle_timings,
                list(self._get_timing(device, i) for i in range(7)),
                list(self._get_timing(function, i) for i in range(6)),
                list(self._get_timing(toggle, i) for i in range(2)),
            )
        ]

        repeat = self._repeat_lead_in[:] + self._repeat_bursts[1][:] + self._repeat_lead_out[:]

        params = dict(
            frequency=self.frequency,
            D=device,
            F=function,
            T=toggle
        )

        code = protocol_base.IRCode(
            self,
            packet[:],
            packet[:] + ([repeat] * repeat_count),
            params,
            repeat_count
        )

        return code

    def _test_decode(self):
        rlc = [
            [
                2340, -780, 780, -780, 780, -780, 780, -780, 780, -780, 780, -1560, 780, -1560, 780, -1560, 780, -1560,
                780, -780, 780, -1560, 780, -1560, 780, -1560, 780, -780, 780, -1560, 780, -1560, 780, -100000
            ],
            [
                2340, -780, 780, -780, 780, -780, 780, -780, 780, -780, 780, -1560, 780, -1560, 780, -1560, 780, -1560,
                780, -780, 780, -1560, 780, -1560, 780, -1560, 780, -780, 780, -1560, 780, -1560, 780, -60000
            ]
        ]

        params = [
            None,
            dict(function=29, toggle=3, device=112)
        ]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(function=29, toggle=3, device=112)
        protocol_base.IrProtocolBase._test_encode(self, params)


Dyson = Dyson()
