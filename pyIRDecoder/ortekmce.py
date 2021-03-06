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


TIMING = 480


class OrtekMCE(protocol_base.IrProtocolBase):
    """
    IR decoder for the OrtekMCE protocol.
    """
    irp = '{38.6k,480,lsb}<1,-1|-1,1>([P=0][P=1][P=2],4,-1,D:5,P:2,F:6,C:4,-48m)+{C=3+#D+#P+#F}'
    frequency = 38600
    bit_count = 17
    encoding = 'lsb'

    _lead_in = [TIMING * 4, -TIMING]
    _lead_out = [-48000]
    _middle_timings = []
    _bursts = [[TIMING, -TIMING], [-TIMING, TIMING]]

    _repeat_lead_in = []
    _repeat_lead_out = []
    _repeat_bursts = []

    _code_order = [
        ['D', 5],
        ['F', 6]
    ]

    _parameters = [
        ['D', 0, 4],
        ['P', 5, 6],
        ['F', 7, 12],
        ['CHECKSUM', 13, 16]
    ]
    # [D:0..31,F:0..63]
    encode_parameters = [
        ['device', 0, 31],
        ['function', 0, 63],
    ]

    def _calc_checksum(self, device, function, p):
        d = self._count_one_bits(device)
        f = self._count_one_bits(function)
        p = self._count_one_bits(p)

        return self._get_bits(3 + d + f + p, 0, 3)

    def decode(self, data, frequency=0):
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)
        checksum = self._calc_checksum(code.device, code.function, code.p)

        if checksum != code.checksum or code.p not in (0, 1, 2):
            raise DecodeError('Checksum failed')

        if len(self._sequence) == 0:
            if code.p != 0:
                raise DecodeError('Invalid frame')
            self._sequence.append(code)
            raise RepeatLeadIn

        if len(self._sequence) == 1:
            if code.p != 1:
                del self._sequence[:]
                raise DecodeError('Invalid frame')

            self._sequence.append(code)
            raise RepeatLeadIn

        if code.p != 2:
            del self._sequence[:]
            raise DecodeError('Invalid frame')

        if self._last_code is not None:
            if self._last_code == code:
                return self._last_code
            self._last_code.repeat_timer.stop()

        self._last_code = code
        return code

    def encode(self, device, function, repeat_count=0):
        codes = []
        
        for p in range(3):
            checksum = self._calc_checksum(
                device,
                function,
                p
            )
            packet = self._build_packet(
                list(self._get_timing(device, i) for i in range(5)),
                list(self._get_timing(p, i) for i in range(2)),
                list(self._get_timing(function, i) for i in range(6)),
                list(self._get_timing(checksum, i) for i in range(4))
            )
            codes += [packet]

        params = dict(
            frequency=self.frequency,
            D=device,
            F=function,
        )

        code = protocol_base.IRCode(
            self,
            codes[:],
            codes[:] * (repeat_count + 1),
            params,
            repeat_count
        )

        return code

    def _test_decode(self):
        rlc = [
            [
                1920, -480, 480, -960, 480, -480, 480, -480, 480, -480, 960, -480, 480, -480, 480, -960, 480, -480, 480, -480,
                480, -480, 480, -480, 960, -480, 480, -960, 480, -480, 480, -48000
            ],
            [
                1920, -480, 480, -960, 480, -480, 480, -480, 480, -480, 480, -480, 960, -480, 480, -960, 480, -480, 480, -480,
                480, -480, 480, -480, 480, -480, 960, -960, 480, -480, 480, -48000
            ],
            [
                1920, -480, 480, -960, 480, -480, 480, -480, 480, -480, 960, -960, 960, -960, 480, -480, 480, -480, 480, -480,
                480, -480, 480, -480, 960, -960, 480, -480, 480, -48000
            ]
        ]

        params = [
            dict(device=30, function=62, p=0),
            dict(device=30, function=62, p=1),
            dict(device=30, function=62, p=2)
        ]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(device=30, function=62)
        protocol_base.IrProtocolBase._test_encode(self, params)


OrtekMCE = OrtekMCE()
