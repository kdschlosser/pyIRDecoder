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


TIMING = 444


class Entone(protocol_base.IrProtocolBase):
    """
    IR decoder for the Entone protocol.
    """
    irp = '{36k,444,msb}<-1,1|1,-1>(6,-2,1:1,M:3,<-2,2|2,-2>(T:1),0xE60396FFFFF:44,F:8,0:4,-131.0m)*{M=6,T=0}'
    frequency = 36000
    bit_count = 61
    encoding = 'msb'

    _lead_in = [TIMING * 6, -TIMING * 2]
    _lead_out = [-131000]
    _middle_timings = [{'start': 4, 'stop': 5, 'bursts': [[-TIMING * 2, TIMING * 2], [TIMING * 2, -TIMING * 2]]}]
    _bursts = [[-TIMING, TIMING], [TIMING, -TIMING]]

    _repeat_lead_in = [TIMING * 16, -TIMING * 8]
    _repeat_lead_out = [TIMING, 108000]
    _repeat_bursts = []

    _code_order = [
        ['F', 8]
    ]

    _parameters = [
        ['C0', 0, 0],
        ['M', 1, 3],
        ['T', 4, 4],
        ['C1', 5, 48],
        ['F', 49, 56],
        ['C2', 57, 60]
    ]
    # [F:0..255]
    encode_parameters = [
        ['function', 0, 255]
    ]

    def decode(self, data, frequency=0):
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)
        if self._last_code is not None:
            if self._last_code == code:
                return self._last_code

            self._last_code.repeat_timer.stop()
            self._last_code = None

        if code.c0 != 1 or code.mode != 6 or code.c1 != 0xE60396FFFFF or code.c2 != 0:
            raise DecodeError('Checksum failed')

        self._last_code = code
        return code

    def encode(self, function, repeat_count=0):
        c0 = 1
        c1 = 0xE60396FFFFF
        c2 = 0
        toggle = 0
        mode = 6

        toggle = self._middle_timings[0]['bursts'][toggle]

        packet = self._build_packet(
            list(self._get_timing(c0, i) for i in range(1)),
            list(self._get_timing(mode, i) for i in range(3)),
            toggle,
            list(self._get_timing(c1, i) for i in range(44)),
            list(self._get_timing(function, i) for i in range(8)),
            list(self._get_timing(c2, i) for i in range(4)),
        )

        params = dict(
            frequency=self.frequency,
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
            2664, -888, 444, -444, 444, -444, 444, -888, 444, -888, 1332, -444, 444, -444, 444, -888, 444, -444,
            888, -444, 444, -888, 444, -444, 444, -444, 444, -444, 444, -444, 444, -444, 444, -444, 888, -444,
            444, -444, 444, -888, 444, -444, 888, -888, 888, -444, 444, -888, 888, -444, 444, -444, 444, -444,
            444, -444, 444, -444, 444, -444, 444, -444, 444, -444, 444, -444, 444, -444, 444, -444, 444, -444,
            444, -444, 444, -444, 444, -444, 444, -444, 444, -444, 444, -444, 444, -444, 444, -444, 444, -444,
            444, -444, 444, -888, 888, -444, 444, -444, 444, -888, 444, -444, 444, -444, 444, -444, 444, -444,
            444, -131000
        ]]

        params = [dict(function=238)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(function=238)
        protocol_base.IrProtocolBase._test_encode(self, params)


Entone = Entone()
