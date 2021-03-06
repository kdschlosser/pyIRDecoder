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


TIMING = 300


class NovaPace(protocol_base.IrProtocolBase):
    """
    IR decoder for the NovaPace protocol.
    """
    irp = '{38k,300,msb}<-1,1|1,-1>(1,-1,D:10,S:8,F:8,(1-T):1,-1,1,-82m)*'
    frequency = 38000
    bit_count = 27
    encoding = 'msb'

    _lead_in = [TIMING, -TIMING]
    _lead_out = [-TIMING, TIMING, -82000]
    _middle_timings = []
    _bursts = [[-TIMING, TIMING], [TIMING, -TIMING]]

    _has_repeat_lead_out = True

    _code_order = [
        ['D', 10],
        ['S', 8],
        ['F', 8],
    ]

    _current_toggle = 0

    _parameters = [
        ['D', 0, 9],
        ['S', 10, 17],
        ['F', 18, 25],
        ['T', 26, 26]
    ]
    # [D:0..1023,S:0..255,F:0..255,T@:0..1=0]
    encode_parameters = [
        ['device', 0, 1023],
        ['sub_device', 0, 255],
        ['function', 0, 255]
    ]

    def decode(self, data, frequency=0):
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)
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
        self._current_toggle = int(not self._current_toggle)

        packet = self._build_packet(
            list(self._get_timing(device, i) for i in range(10)),
            list(self._get_timing(sub_device, i) for i in range(8)),
            list(self._get_timing(function, i) for i in range(8)),
            list(self._get_timing(self._current_toggle, i) for i in range(1))
        )

        params = dict(
            frequency=self.frequency,
            D=device,
            S=sub_device,
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
        rlc = [[
            300, -600, 600, -600, 600, -600, 300, -300, 600, -300, 300, -300, 300, -300, 300, -600, 600, -600,
            300, -300, 600, -600, 300, -300, 300, -300, 600, -300, 300, -300, 300, -300, 300, -600, 300, -300,
            300, -300, 600, -300, 300, -600, 300, -82000
        ]]

        params = [dict(sub_device=72, function=241, toggle=1, device=335)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(sub_device=72, function=241, toggle=1, device=335)
        protocol_base.IrProtocolBase._test_encode(self, params)


NovaPace = NovaPace()
