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


TIMING = 400


class SharpDVD(protocol_base.IrProtocolBase):
    """
    IR decoder for the SharpDVD protocol.
    """
    irp = '{38k,400,lsb}<1,-1|1,-3>(8,-4,170:8,90:8,15:4,D:4,S:8,F:8,E:4,C:4,1,-48)*{C=D^S:4:0^S:4:4^F:4:0^F:4:4^E:4}'
    frequency = 38000
    bit_count = 48
    encoding = 'lsb'

    _lead_in = [TIMING * 8, -TIMING * 4]
    _lead_out = [TIMING, -TIMING * 48]
    _middle_timings = []
    _bursts = [[TIMING, -TIMING], [TIMING, -TIMING * 3]]

    _code_order = [
        ['D', 4],
        ['S', 8],
        ['F', 8],
        ['E', 4]
    ]

    _parameters = [
        ['C0', 0, 7],
        ['C1', 8, 15],
        ['C2', 16, 19],
        ['D', 20, 23],
        ['S', 24, 31],
        ['F', 32, 39],
        ['E', 40, 43],
        ['CHECKSUM', 44, 47]
    ]
    # [D:0..15,S:0..255,F:0..255,E:0..15=1]
    encode_parameters = [
        ['device', 0, 15],
        ['sub_device', 0, 255],
        ['function', 0, 255],
        ['extended_function', 0, 15]
    ]

    def _calc_checksum(self, device, sub_device, function, extended_function):
        f1 = self._get_bits(function, 0, 3)
        f2 = self._get_bits(function, 4, 7)
        s1 = self._get_bits(sub_device, 0, 3)
        s2 = self._get_bits(sub_device, 4, 7)
        e = self._get_bits(extended_function, 0, 3)

        return device ^ s1 ^ s2 ^ f1 ^ f2 ^ e

    def decode(self, data, frequency=0):
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)

        if self._last_code is not None:
            if self._last_code == code:
                return self._last_code

            self._last_code.repeat_timer.stop()
            self._last_code = None

        checksum = self._calc_checksum(
            code.device,
            code.sub_device,
            code.function,
            code.extended_function
        )

        if code.c0 != 170 or code.c1 != 90 or code.c2 != 15 or checksum != code.checksum:
            raise DecodeError('Checksum failed')

        self._last_code = code
        return code

    def encode(self, device, sub_device, function, extended_function, repeat_count=0):
        checksum = self._calc_checksum(
            device,
            sub_device,
            function,
            extended_function
        )

        c0 = 170
        c1 = 90
        c2 = 15

        packet = self._build_packet(
            list(self._get_timing(c0, i) for i in range(8)),
            list(self._get_timing(c1, i) for i in range(8)),
            list(self._get_timing(c2, i) for i in range(4)),
            list(self._get_timing(device, i) for i in range(4)),
            list(self._get_timing(sub_device, i) for i in range(8)),
            list(self._get_timing(function, i) for i in range(8)),
            list(self._get_timing(extended_function, i) for i in range(4)),
            list(self._get_timing(checksum, i) for i in range(4))
        )

        params = dict(
            frequency=self.frequency,
            D=device,
            S=sub_device,
            F=function,
            E=extended_function
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
            3200, -1600, 400, -400, 400, -1200, 400, -400, 400, -1200, 400, -400, 400, -1200, 
            400, -400, 400, -1200, 400, -400, 400, -1200, 400, -400, 400, -1200, 400, -1200, 
            400, -400, 400, -1200, 400, -400, 400, -1200, 400, -1200, 400, -1200, 400, -1200, 
            400, -1200, 400, -1200, 400, -400, 400, -1200, 400, -400, 400, -400, 400, -400, 
            400, -1200, 400, -1200, 400, -1200, 400, -400, 400, -1200, 400, -1200, 400, -400, 
            400, -1200, 400, -400, 400, -400, 400, -400, 400, -400, 400, -400, 400, -400, 
            400, -1200, 400, -400, 400, -1200, 400, -1200, 400, -1200, 400, -1200, 400, -400, 
            400, -19200, 
        ]]

        params = [dict(function=5, sub_device=184, device=11, extended_function=10)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(function=5, sub_device=184, device=11, extended_function=10)
        protocol_base.IrProtocolBase._test_encode(self, params)


SharpDVD = SharpDVD()
