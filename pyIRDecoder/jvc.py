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


TIMING = 527


class JVC(protocol_base.IrProtocolBase):
    """
    IR decoder for the JVC protocol.
    """
    irp = '{37.9k,527,lsb}<1,-1|1,-3>(16,-8,D:8,F:8,1,^59.08m,(D:8,F:8,1,^46.42m)*)'
    frequency = 37900
    bit_count = 16
    encoding = 'lsb'

    _lead_in = [TIMING * 16, -TIMING * 8]
    _lead_out = [TIMING, 59080]
    _middle_timings = []
    _bursts = [[TIMING, -TIMING], [TIMING, -TIMING * 3]]

    _repeat_lead_in = []
    _repeat_lead_out = [TIMING, 46420]
    _repeat_bursts = [[TIMING, -TIMING], [TIMING, -TIMING * 3]]

    _code_order = [
        ['D', 8],
        ['F', 8],
    ]

    _parameters = [
        ['D', 0, 7],
        ['F', 8, 15],
    ]
    # [D:0..255,F:0..255]
    encode_parameters = [
        ['device', 0, 255],
        ['function', 0, 255]
    ]

    def encode(self, device, function, repeat_count=0):
        lead_in = self._lead_in[:]
        lead_out = self._lead_out[:]

        packet = [
            self._build_packet(
                list(self._get_timing(device, i) for i in range(8)),
                list(self._get_timing(function, i) for i in range(8))
            )
        ]

        del self._lead_in[:]
        self._lead_out = self._repeat_lead_out[:]

        repeat = self._build_packet(
            list(self._get_timing(device, i) for i in range(8)),
            list(self._get_timing(function, i) for i in range(8))
        )

        self._lead_in = lead_in[:]
        self._lead_out = lead_out[:]

        params = dict(
            frequency=self.frequency,
            D=device,
            F=function,
        )

        code = protocol_base.IRCode(
            self,
            [packet[:]],
            [packet[:]] + ([repeat[:]] * repeat_count),
            params,
            repeat_count
        )

        return code

    def _test_decode(self):
        rlc = [[
            8432, -4216, 527, -527, 527, -527, 527, -527, 527, -527, 527, -527, 527, -1581, 527, -527, 527, -1581,
            527, -527, 527, -527, 527, -527, 527, -527, 527, -527, 527, -1581, 527, -527, 527, -1581, 527, -24825
        ]]

        params = [dict(device=160, function=160)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(device=160, function=160)
        protocol_base.IrProtocolBase._test_encode(self, params)


JVC = JVC()
