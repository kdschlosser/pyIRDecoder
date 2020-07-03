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
from . import DecodeError


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
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)

        if code.device != code.d2 or code.function != code.f2:
            raise DecodeError('Checksum failed')

        params = dict(
            D=code.device,
            F=code.function,
            T=self._reverse_bits(code.toggle, 2),
            frequency=self.frequency
        )

        return protocol_base.IRCode(
            self,
            code.original_rlc,
            code.normalized_rlc,
            params
        )

    def encode(self, device, function, toggle):
        toggle = self._reverse_bits(toggle, 2)

        packet = self._build_packet(
            list(self._get_timing(device, i) for i in range(7)),
            list(self._get_timing(function, i) for i in range(6)),
            list(self._get_timing(toggle, i) for i in range(2)),
            self._middle_timings,
            list(self._get_timing(device, i) for i in range(7)),
            list(self._get_timing(function, i) for i in range(6)),
            list(self._get_timing(toggle, i) for i in range(2)),
        )

        return [packet]

    def _test_decode(self):
        rlc = [[
            2340, -780, 780, -780, 780, -780, 780, -780, 780, -780, 780, -1560, 780, -1560, 780, -1560, 780, -1560,
            780, -780, 780, -1560, 780, -1560, 780, -1560, 780, -780, 780, -1560, 780, -1560, 780, -100000,
            2340, -780, 780, -780, 780, -780, 780, -780, 780, -780, 780, -1560, 780, -1560, 780, -1560, 780, -1560,
            780, -780, 780, -1560, 780, -1560, 780, -1560, 780, -780, 780, -1560, 780, -1560, 780, -60000
        ]]

        params = [dict(function=29, toggle=3, device=112)]

        protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(function=29, toggle=3, device=112)
        protocol_base.IrProtocolBase._test_encode(self, params)


Dyson = Dyson()
