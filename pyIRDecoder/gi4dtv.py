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


TIMING = 992


class GI4DTV(protocol_base.IrProtocolBase):
    """
    IR decoder for the GI4DTV protocol.
    """
    irp = (
        '{37.3k,992,lsb}<1,-1|1,-3>(5,-2,F:6,D:2,C0:1,C1:1,C2:1,C3:1,1,-60)*'
        '{C0=D:1:2+#(F&25)+#(D&1),C1=D:1:2+#(F&43)+#(D&3),C2=D:1:2+#(F&22)+#(D&3),C3=D:1:2+#(F&44)+#(D&2)}'
    )
    frequency = 37300
    bit_count = 12
    encoding = 'lsb'

    _lead_in = [TIMING * 5, -TIMING * 2]
    _lead_out = [TIMING, -TIMING * 60]
    _middle_timings = []
    _bursts = [[TIMING, -TIMING], [TIMING, -TIMING * 3]]

    _code_order = [
        ['F', 6],
        ['D', 2]
    ]

    _parameters = [
        ['F', 0, 5],
        ['D', 6, 7],
        ['C0', 8, 8],
        ['C1', 9, 9],
        ['C2', 10, 10],
        ['C3', 11, 11]
    ]
    # [D:0..7,F:0..63]
    encode_parameters = [
        ['device', 0, 7],
        ['function', 0, 63],
    ]

    def _calc_checksum(self, device, function):
        # C0=D:1:2+#(F&25)+#(D&1)
        # C1=D:1:2+#(F&43)+#(D&3)
        # C2=D:1:2+#(F&22)+#(D&3)
        # C3=D:1:2+#(F&44)+#(D&2)
        d = self._get_bit(device, 1)

        c0 = d + self._count_one_bits(function & 25) + self._count_one_bits(device & 1)
        c1 = d + self._count_one_bits(function & 43) + self._count_one_bits(device & 3)
        c2 = d + self._count_one_bits(function & 22) + self._count_one_bits(device & 3)
        c3 = d + self._count_one_bits(function & 44) + self._count_one_bits(device & 2)

        return (
            int(not self._get_bit(c0, 0)),
            int(not self._get_bit(c1, 0)),
            int(not self._get_bit(c2, 0)),
            int(not self._get_bit(c3, 0))
        )

    def decode(self, data, frequency=0):
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)

        if self._last_code is not None:
            if self._last_code == code:
                return self._last_code

            self._last_code.repeat_timer.stop()
            self._last_code = None

        c0, c1, c2, c3 = self._calc_checksum(code.device, code.function)

        if c0 != code.c0 or c1 != code.c1 or c2 != code.c2 or c3 != code.c3:
            raise DecodeError('Checksum failed')

        self._last_code = code
        return code

    def encode(self, device, function, repeat_count=0):
        c0, c1, c2, c3 = self._calc_checksum(device, function)

        packet = self._build_packet(
            list(self._get_timing(function, i) for i in range(6)),
            list(self._get_timing(device, i) for i in range(2)),
            list(self._get_timing(c0, i) for i in range(1)),
            list(self._get_timing(c1, i) for i in range(1)),
            list(self._get_timing(c2, i) for i in range(1)),
            list(self._get_timing(c3, i) for i in range(1))
        )

        params = dict(
            frequency=self.frequency,
            D=device,
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
            4960, -1984, 992, -2976, 992, -992, 992, -992, 992, -992, 992, -2976, 992, -2976, 992, -2976,
            992, -2976, 992, -2976, 992, -992, 992, -2976, 992, -992, 992, -59520
        ]]

        params = [dict(device=3, function=49)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(device=3, function=49)
        protocol_base.IrProtocolBase._test_encode(self, params)


GI4DTV = GI4DTV()
