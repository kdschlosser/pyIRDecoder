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

    _repeat_lead_in = [TIMING * 3, -TIMING]
    _repeat_lead_out = [TIMING, -60000]
    _repeat_bursts = [[TIMING, -TIMING], [TIMING, -TIMING * 3]]

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
        try:
            code = protocol_base.IrProtocolBase.decode(self, data, frequency)
            if isinstance(self._last_code, protocol_base.IRCode):
                if self._last_code == code:
                    if self._last_code._code.get_bits(0, 0) != 1:
                        self._last_code.repeat_timer.start()
                        raise RepeatLeadIn

                    return self._last_code
                else:
                    self._last_code.repeat_timer.stop()

            if code.device != code.d2 or code.function != code.f2:
                self._last_code = None
                raise DecodeError('Checksum failed')

            params = dict(
                D=code.device,
                F=code.function,
                T=self._reverse_bits(code.toggle, 2),
                frequency=self.frequency
            )

            code = protocol_base.IRCode(
                self,
                code.original_rlc,
                code.normalized_rlc,
                params
            )

            self._last_code = code
            return code

        except DecodeError:
            if isinstance(self._last_code, dict):
                try:
                    code = protocol_base.code_wrapper.CodeWrapper(
                        self.encoding,
                        self._lead_in[:],
                        self._lead_out[:],
                        [],
                        self._bursts[:],
                        self.tolerance,
                        data[:]
                    )
                except DecodeError:
                    self._last_code = None
                    raise

                params = dict(
                    frequency=self.frequency
                )

                for key, start, stop in self._parameters[:3]:
                    params[key] = code.get_value(start, stop)

                if self._last_code == params:
                    params['T'] = self._reverse_bits(params['T'], 2)
                    code = protocol_base.IRCode(
                        self,
                        code.original_code,
                        list(code),
                        params
                    )
                    self._last_code = code
                    return code
                else:
                    self._last_code = None
                    raise DecodeError('Invalid frame')

            code = protocol_base.code_wrapper.CodeWrapper(
                self.encoding,
                self._lead_in[:],
                list(self._middle_timings[0]),
                [],
                self._bursts[:],
                self.tolerance,
                data[:]
            )

            params = dict(
                frequency=self.frequency
            )

            for key, start, stop in self._parameters[:3]:
                params[key] = code.get_value(start, stop)

            self._last_code = params
            raise RepeatLeadIn

    def encode(self, device, function, toggle, repeat_count=0):
        toggle = self._reverse_bits(toggle, 2)

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

        repeat = self._repeat_lead_in[:] + self._repeat_bursts[1] + self._repeat_lead_out
        packet += [repeat] * repeat_count

        return packet

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
