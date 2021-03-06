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


TIMING = 1000 / 35.7


class Rs200(protocol_base.IrProtocolBase):
    """
    IR decoder for the Rs200 protocol.
    """
    irp = (
        '{35.7k,1,msb}<50p,-120p|21p,-120p>(25:6,(H4-1):2,(H3-1):2,(H2-1):2,(H1-1):2,P:1,(D-1):3,F:2,0:2,sum_:4,-1160p)*'
        '{P=~(#(D-1)+#F):1,sum_=9+((H4-1)*4+(H3-1))+((H2-1)*4+(H1-1))+(P*8+(D-1))+F*4}'
    )
    frequency = 35700
    bit_count = 26
    encoding = 'msb'

    _lead_in = []
    _lead_out = [int(-TIMING * 1160)]
    _middle_timings = []
    _bursts = [[int(TIMING * 50), int(-TIMING * 120)], [int(TIMING * 21), int(-TIMING * 120)]]

    _code_order = [
        ['H4', 2],
        ['H3', 2],
        ['H2', 2],
        ['H1', 2],
        ['D', 3],
        ['F', 2]
    ]

    _parameters = [
        ['C0', 0, 5],
        ['H4', 6, 7],
        ['H3', 8, 9],
        ['H2', 10, 11],
        ['H1', 12, 13],
        ['P', 14, 14],
        ['D', 15, 17],
        ['F', 18, 19],
        ['C1', 20, 21],
        ['CHECKSUM', 22, 25]
    ]
    # [H1:1..4,H2:1..4,H3:1..4,H4:1..4,D:1..6,F:0..2]
    encode_parameters = [
        ['device', 1, 6],
        ['function', 0, 2],
        ['h1', 1, 4],
        ['h2', 1, 4],
        ['h3', 1, 4],
        ['h4', 1, 4],
    ]

    def _calc_checksum(self, device, function, h1, h2, h3, h4):
        # {P=~(#(D-1)+#F):1,
        # sum_=9+((H4-1)*4+(H3-1))+((H2-1)*4+(H1-1))+(P*8+(D-1))+F*4}

        p = int(not self._get_bit(self._count_one_bits(device) + self._count_one_bits(function), 0))
        sum_ = 9 + ((h4 - 1) * 4 + (h3 - 1)) + ((h2 - 1) * 4 + (h1 - 1)) + (p * 8 + (device - 1)) + function * 4
        
        return p, self._get_bits(sum_, 0, 3)

    def decode(self, data, frequency=0):
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)
        p, checksum = self._calc_checksum(code.device, code.function, code.h1, code.h2, code.h3, code.h4)

        if checksum != code.checksum or p != code.p or code.c0 != 25 or code.c1 != 0:
            raise DecodeError('Checksum failed')
        
        params = dict(
            D=code.device + 1,
            F=code.function,
            H1=code.h1 + 1,
            H2=code.h2 + 1,
            H3=code.h3 + 1,
            H4=code.H4 + 1,
            frequency=self.frequency
        )

        code = protocol_base.IRCode(self, code.original_rlc, code.normalized_rlc, params)

        if self._last_code is not None:
            if self._last_code == code:
                return self._last_code

            self._last_code.repeat_timer.stop()

        self._last_code = code
        return code

    def encode(self, device, function, h1, h2, h3, h4, repeat_count=0):
        c0 = 25
        c1 = 0
        h1 -= 1
        h2 -= 1
        h3 -= 1
        h4 -= 1
        device -= 1
        
        p, checksum = self._calc_checksum(
            device,
            function,
            h1, 
            h2, 
            h3, 
            h4
        )

        packet = self._build_packet(
            list(self._get_timing(c0, i) for i in range(6)),
            list(self._get_timing(h4, i) for i in range(2)),
            list(self._get_timing(h3, i) for i in range(2)),
            list(self._get_timing(h2, i) for i in range(2)),
            list(self._get_timing(h1, i) for i in range(2)),
            list(self._get_timing(p, i) for i in range(1)),
            list(self._get_timing(device, i) for i in range(3)),
            list(self._get_timing(function, i) for i in range(2)),
            list(self._get_timing(c1, i) for i in range(1)),
            list(self._get_timing(checksum, i) for i in range(4)),
        )

        params = dict(
            frequency=self.frequency,
            D=device,
            F=function,
            H1=h1,
            H2=h2,
            H3=h3,
            H4=h4
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
            1401, -3361, 588, -3361, 588, -3361, 1401, -3361, 1401, -3361, 588, -3361, 1401, -3361, 
            588, -3361, 1401, -3361, 588, -3361, 1401, -3361, 1401, -3361, 588, -3361, 1401, -3361, 
            588, -3361, 1401, -3361, 588, -3361, 588, -3361, 1401, -3361, 1401, -3361, 1401, -3361, 
            1401, -3361, 588, -3361, 1401, -3361, 588, -3361, 588, -35854, 
        ]]

        params = [dict(function=0, device=4, h2=1, h3=2, h1=3, h4=2)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(function=0, device=4, h2=1, h3=2, h1=3, h4=2)
        protocol_base.IrProtocolBase._test_encode(self, params)


Rs200 = Rs200()
