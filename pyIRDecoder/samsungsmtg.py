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


TIMING = 497


class SamsungSMTG(protocol_base.IrProtocolBase):
    """
    IR decoder for the SamsungSMTG protocol.
    """
    irp = '{38.5k,497,msb}<1,-1|1,-3>(4497u,-4497u,D:16,1,-4497u,S:4,F:16,1,^120m)*'
    frequency = 38500
    bit_count = 36
    encoding = 'msb'

    _lead_in = [4497, -4497]
    _lead_out = [TIMING, 120000]
    _middle_timings = [(TIMING, -4497)]
    _bursts = [[TIMING, -TIMING], [TIMING, -TIMING * 3]]

    _code_order = [
        ['D', 16],
        ['S', 4],
        ['F', 16],
    ]

    _parameters = [
        ['D', 0, 15],
        ['S', 16, 19],
        ['F', 20, 35]
    ]
    # [D:0..65335,S:0..15,F:0..65535]
    encode_parameters = [
        ['device', 0, 65335],
        ['sub_device', 0, 15],
        ['function', 0, 65335],
    ]

    def encode(self, device, sub_device, function, repeat_count=0):

        packet = self._build_packet(
            list(self._get_timing(device, i) for i in range(16)),
            self._middle_timings,
            list(self._get_timing(sub_device, i) for i in range(4)),
            list(self._get_timing(function, i) for i in range(16))
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
            4497, -4497, 497, -1491, 497, -1491, 497, -1491, 497, -497, 497, -1491, 497, -497,
            497, -1491, 497, -497, 497, -1491, 497, -497, 497, -1491, 497, -497, 497, -497,
            497, -1491, 497, -497, 497, -1491, 497, -4497, 497, -1491, 497, -1491, 497, -1491,
            497, -1491, 497, -497, 497, -1491, 497, -497, 497, -1491, 497, -497, 497, -497,
            497, -1491, 497, -1491, 497, -1491, 497, -497, 497, -497, 497, -497, 497, -497,
            497, -1491, 497, -1491, 497, -1491, 497, -48857,
        ]]

        params = [dict(device=60069, function=21383, sub_device=15)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(device=60069, function=21383, sub_device=15)
        protocol_base.IrProtocolBase._test_encode(self, params)


SamsungSMTG = SamsungSMTG()
