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


TIMING = 432


class DenonK(protocol_base.IrProtocolBase):
    """
    IR decoder for the DenonK protocol.
    """
    irp = '{37k,432,lsb}<1,-1|1,-3>(8,-4,84:8,50:8,0:4,D:4,S:4,F:12,((D*16)^S^(F*16)^(F:8:4)):8,1,-173)*'
    frequency = 37000
    bit_count = 48
    encoding = 'lsb'

    _lead_in = [TIMING * 8, -TIMING * 4]
    _lead_out = [TIMING, -TIMING * 173]
    _bursts = [[TIMING, -TIMING], [TIMING, -TIMING * 3]]

    _code_order = [
        ['D', 4],
        ['S', 4],
        ['F', 12]
    ]

    _parameters = [
        ['C0', 0, 7],
        ['C1', 8, 15],
        ['C2', 16, 19],
        ['D', 20, 23],
        ['S', 24, 27],
        ['F', 28, 39],
        ['CHECKSUM', 40, 47]
    ]
    # [D:0..15,S:0..15,F:0..4095]
    encode_parameters = [
        ['device', 0, 15],
        ['sub_device', 0, 15],
        ['function', 0, 4095],
    ]

    def _calc_checksum(self, device, sub_device, function):
        # ((D*16)^S^(F*16)^(F:8:4))
        d = device * 16
        f1 = function * 16
        f2 = self._get_bits(function, 3, 10)

        c = d ^ sub_device ^ f1 ^ f2
        c = self._get_bits(c, 0, 7)
        return c

    def decode(self, data, frequency=0):
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)
        checksum = self._calc_checksum(code.device, code.sub_device, code.function)

        if self._last_code is not None:
            if code == self._last_code:
                return self._last_code

            self._last_code.repeat_timer.stop()

        if code.c0 != 84 or code.c1 != 50 or code.c2 != 0:
            raise DecodeError('Checksum failed')

        self._last_code = code
        return code

    def encode(self, device, sub_device, function, repeat_count=0):
        c0 = 84
        c1 = 50
        c2 = 0
        checksum = self._calc_checksum(device, sub_device, function)

        packet = self._build_packet(
            list(self._get_timing(c0, i) for i in range(8)),
            list(self._get_timing(c1, i) for i in range(8)),
            list(self._get_timing(c2, i) for i in range(4)),
            list(self._get_timing(device, i) for i in range(4)),
            list(self._get_timing(sub_device, i) for i in range(4)),
            list(self._get_timing(function, i) for i in range(12)),
            list(self._get_timing(checksum, i) for i in range(8))
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
            3456, -1728, 432, -432, 432, -432, 432, -1296, 432, -432, 432, -1296, 432, -432, 432, -1296, 432, -432,
            432, -432, 432, -1296, 432, -432, 432, -432, 432, -1296, 432, -1296, 432, -432, 432, -432, 432, -432,
            432, -432, 432, -432, 432, -432, 432, -1296, 432, -1296, 432, -432, 432, -432, 432, -1296, 432, -432,
            432, -1296, 432, -1296, 432, -432, 432, -432, 432, -432, 432, -432, 432, -432, 432, -432, 432, -432,
            432, -1296, 432, -1296, 432, -432, 432, -432, 432, -432, 432, -1296, 432, -432, 432, -1296, 432, -432,
            432, -432, 432, -1296, 432, -432, 432, -432, 432, -74736
        ]]

        params = [dict(device=3, function=384, sub_device=13)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(device=3, function=384, sub_device=13)
        protocol_base.IrProtocolBase._test_encode(self, params)


DenonK = DenonK()
