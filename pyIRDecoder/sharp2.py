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


TIMING = 264

# [[264, -1848, 264, -1848, 264, -792, 264, -1848, 264, -1848, 264, -792, 264, -792, 264, -1848, 264, -792, 264, -792, 264, -1848, 264, -1848, 264, -792, 264, -792, 264, -1848, 264, -43560]]
# [[264, -1848, 264, -1848, 264, -792, 264, -1848, 264, -1848, 264, -792, 264, -792, 264, -1848, 264, -792, 264, -792, 264, -1848, 264, -1848, 264, -1848, 264, -792, 264, -1848, 264, -43560]]
class Sharp2(protocol_base.IrProtocolBase):
    """
    IR decoder for the Sharp2 protocol.
    """
    irp = '{38k,264,lsb}<1,-3|1,-7>(D:5,~F:8,2:2,1,-165)*'
    frequency = 38000
    bit_count = 15
    encoding = 'lsb'

    _lead_in = []
    _lead_out = [TIMING,  -TIMING * 165]
    _middle_timings = []
    _bursts = [[TIMING, -TIMING * 3], [TIMING, -TIMING * 7]]

    _code_order = [
        ['D', 5],
        ['F', 8],
    ]

    _parameters = [
        ['D', 0, 4],
        ['F', 5, 12],
        ['C0', 13, 14],
    ]
    # [D:0..31,F:0..255]
    encode_parameters = [
        ['device', 0, 31],
        ['function', 0, 255],
    ]

    def decode(self, data, frequency=0):
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)

        if code.c0 != 2:
            raise DecodeError('Checksum failed')

        function = self._invert_bits(code.function, 8)

        params = dict(
            D=code.device,
            F=function,
            C0=code.c0
        )

        code = protocol_base.IRCode(self, code.original_rlc, code.normalized_rlc, params)

        if self._last_code is not None:
            if self._last_code == code:
                return self._last_code

            self._last_code.repeat_timer.stop()
            self._last_code = None

        self._last_code = code
        return code

    def encode(self, device, function, repeat_count=0):
        c0 = 2

        func = self._invert_bits(function, 8)

        packet = self._build_packet(
            list(self._get_timing(device, i) for i in range(5)),
            list(self._get_timing(func, i) for i in range(8)),
            list(self._get_timing(c0, i) for i in range(2)),
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
            264, -1848, 264, -1848, 264, -792, 264, -792, 264, -1848, 264, -792, 264, -1848, 
            264, -1848, 264, -792, 264, -1848, 264, -792, 264, -792, 264, -792, 264, -792, 
            264, -1848, 264, -43560, 
        ]]

        params = [dict(device=19, function=233)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(device=19, function=233)
        protocol_base.IrProtocolBase._test_encode(self, params)


Sharp2 = Sharp2()
