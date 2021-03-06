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


class F12(protocol_base.IrProtocolBase):
    """
    IR decoder for the F12 protocol.
    """
    irp = '{37.9k,422,lsb}<1,-3|3,-1>((D:3,S:1,F:8,-80)2)*'
    frequency = 37900
    bit_count = 12
    encoding = 'lsb'

    _lead_in = []
    _lead_out = [-TIMING * 80]
    _middle_timings = []
    _bursts = [[TIMING, -TIMING * 3], [TIMING * 3, -TIMING]]

    _repeat_lead_in = []
    _repeat_lead_out = []
    _repeat_bursts = []

    _code_order = [
        ['D', 3],
        ['S', 1],
        ['F', 8]
    ]

    _parameters = [
        ['D', 0, 2],
        ['S', 3, 3],
        ['F', 4, 11],
    ]
    # [D:0..7,S:0..1,F:0..255]
    encode_parameters = [
        ['device', 0, 7],
        ['sub_device', 0, 1],
        ['function', 0, 255],
    ]

    def decode(self, data, frequency=0):
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)

        if self._sequence:
            code2 = self._sequence[0]
            del self._sequence[:]

            if (
                code2.device != code.device or
                code2.function != code.function or
                code2.sub_device != code.sub_device
            ):
                if self._last_code is not None:
                    self._last_code.repeat_timer.stop()
                    self._last_code = None

                raise DecodeError('code does not match lead in')

            if self._last_code is not None:
                if self._last_code == code:
                    return self._last_code

                self._last_code.repeat_timer.stop()
                self._last_code = None

            self._last_code = code
            return self._last_code

        self._sequence.append(code)
        raise RepeatLeadIn

    def encode(self, device, sub_device, function, repeat_count=0):
        packet = self._build_packet(
            list(self._get_timing(device, i) for i in range(3)),
            list(self._get_timing(sub_device, i) for i in range(1)),
            list(self._get_timing(function, i) for i in range(8))
        )

        params = dict(
            frequency=self.frequency,
            D=device,
            S=sub_device,
            F=function,
        )

        code = protocol_base.IRCode(
            self,
            [packet[:], packet[:]],
            [packet[:], packet[:]] * (repeat_count + 1),
            params,
            repeat_count
        )

        return code

    def _test_decode(self):
        rlc = [
            [
                1266, -422, 422, -1266, 1266, -422, 1266, -422, 422, -1266, 422, -1266, 1266, -422, 422, -1266,
                422, -1266, 1266, -422, 1266, -422, 1266, -34182
            ],
            [
                1266, -422, 422, -1266, 1266, -422, 1266, -422,
                422, -1266, 422, -1266, 1266, -422, 422, -1266, 422, -1266, 1266, -422, 1266, -422, 1266, -34182
            ]
        ]

        params = [None, dict(device=5, function=228, sub_device=1)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(device=5, function=228, sub_device=1)
        protocol_base.IrProtocolBase._test_encode(self, params)


F12 = F12()
