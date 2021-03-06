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
from . import RepeatLeadOut

TIMING = 889


class RC5x(protocol_base.IrProtocolBase):
    """
    IR decoder for the RC5x protocol.
    """
    irp = '{36k,889,msb}<1,-1|-1,1>(1,~S:1:6,(1-(T:1)),D:5,-4,S:6,F:6,^114m)*'
    frequency = 36000
    bit_count = 19
    encoding = 'msb'

    _lead_in = [TIMING]
    _lead_out = [114000]
    _middle_timings = [-TIMING * 4]
    _bursts = [[TIMING, -TIMING], [-TIMING, TIMING]]

    _has_repeat_lead_out = True

    _code_order = [
        ['D', 5],
        ['S', 6],
        ['F', 6],
    ]

    _parameters = [
        ['S1', 0, 0],
        ['T', 1, 1],
        ['D', 2, 6],
        ['S', 7, 12],
        ['F', 13, 18]
    ]
    # [D:0..31,S:0..127,F:0..63,T@:0..1=0]
    encode_parameters = [
        ['device', 0, 31],
        ['sub_device', 0, 127],
        ['function', 0, 63]
    ]

    def decode(self, data, frequency=0):
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)

        params = dict(
            D=code.device,
            F=code.function,
            S=self._set_bit(code.sub_device, 6, not self._get_bit(code.s1, 0)),
            T=code.toggle,
            frequency=self.frequency
        )

        code = protocol_base.IRCode(self, code.original_rlc, code.normalized_rlc, params)

        if self._last_code is not None:
            if (
                self._last_code == code and
                self._last_code.toggle == code.toggle
            ):
                return self._last_code

            last_code = self._last_code
            self._last_code.repeat_timer.stop()

            if last_code == code:
                raise RepeatLeadOut

        self._last_code = code
        return code

    def encode(self, device, sub_device, function, repeat_count=0):
        toggle = 0
        s1 = int(not (self._get_bit(sub_device, 6)))

        packet = self._build_packet(
            list(self._get_timing(s1, i) for i in range(1)),
            list(self._get_timing(toggle, i) for i in range(1)),
            list(self._get_timing(device, i) for i in range(5)),
            self._middle_timings,
            list(self._get_timing(sub_device, i) for i in range(6)),
            list(self._get_timing(function, i) for i in range(6)),
        )

        toggle = 1

        lead_out = self._build_packet(
            list(self._get_timing(s1, i) for i in range(1)),
            list(self._get_timing(toggle, i) for i in range(1)),
            list(self._get_timing(device, i) for i in range(5)),
            self._middle_timings,
            list(self._get_timing(sub_device, i) for i in range(6)),
            list(self._get_timing(function, i) for i in range(6)),
        )

        params = dict(
            frequency=self.frequency,
            D=device,
            S=sub_device,
            F=function,
        )

        code = protocol_base.IRCode(
            self,
            [packet[:], lead_out[:]],
            ([packet[:]] * (repeat_count + 1)) + [lead_out[:]],
            params,
            repeat_count
        )

        return code

    def _test_decode(self):
        rlc = [[
            1778, -1778, 1778, -889, 889, -1778, 889, -889, 889, -889, 889, -4445, 1778, -1778,
            1778, -889, 889, -889, 889, -1778, 1778, -889, 889, -1778, 1778, -1778, 889, -75773,
        ]]

        params = [dict(function=37, toggle=1, device=7, sub_device=104)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(function=37, toggle=1, device=7, sub_device=104)
        protocol_base.IrProtocolBase._test_encode(self, params)


RC5x = RC5x()

