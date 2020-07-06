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


TIMING = 500


class Thomson7(protocol_base.IrProtocolBase):
    """
    IR decoder for the Thomson7 protocol.
    """
    irp = '{33k,500,lsb}<1,-4|1,-9>(D:4,(1-T):1,F:7,1,^80m)*'
    frequency = 33000
    bit_count = 12
    encoding = 'lsb'

    _lead_in = []
    _lead_out = [TIMING, 80000]
    _middle_timings = []
    _bursts = [[TIMING, -TIMING * 4], [TIMING, -TIMING * 9]]

    _repeat_lead_in = []
    _repeat_lead_out = []
    _repeat_bursts = []

    # D:4,(1-T):1,D:1:4,F:6
    _parameters = [
        ['D', 0, 3],
        ['T', 4, 4],
        ['F', 5, 11],
    ]
    # [D:0..15,F:0..127,T@:0..1=0]
    encode_parameters = [
        ['device', 0, 15],
        ['function', 0, 127],
        ['toggle', 0, 1]
    ]

    def encode(self, device, function, toggle):

        packet = self._build_packet(
            list(self._get_timing(device, i) for i in range(4)),
            list(self._get_timing(toggle, i) for i in range(1)),
            list(self._get_timing(function, i) for i in range(7))
        )

        return [packet]

    def _test_decode(self):
        rlc = [[
            500, -2000, 500, -2000, 500, -4500, 500, -2000, 500, -2000, 500, -2000, 500, -4500, 
            500, -2000, 500, -4500, 500, -2000, 500, -2000, 500, -2000, 500, -42000, 
        ]]

        params = [dict(function=10, toggle=0, device=4)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(function=10, toggle=0, device=4)
        protocol_base.IrProtocolBase._test_encode(self, params)


Thomson7 = Thomson7()