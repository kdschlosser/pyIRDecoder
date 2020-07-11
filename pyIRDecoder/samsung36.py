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


TIMING = 560


class Samsung36(protocol_base.IrProtocolBase):
    """
    IR decoder for the Samsung36 protocol.
    """
    irp = '{37.9k,560,lsb}<1,-1|1,-3>(4500u,-4500u,D:8,S:8,1,-9,E:4,F:8,~F:8,1,^108m)*'
    frequency = 37900
    bit_count = 36
    encoding = 'lsb'

    _lead_in = [4500, -4500]
    _lead_out = [TIMING, 108000]
    _middle_timings = [(TIMING, -TIMING * 9)]
    _bursts = [[TIMING, -TIMING], [TIMING, -TIMING * 3]]

    _code_order = [
        ['D', 8],
        ['S', 8],
        ['E', 4],
        ['F', 8]
    ]

    _parameters = [
        ['D', 0, 7],
        ['S', 8, 15],
        ['E', 16, 19],
        ['F', 20, 27],
        ['CHECKSUM', 28, 35],
    ]
    # [D:0..255,S:0..255,F:0..255,E:0..15]
    encode_parameters = [
        ['device', 0, 255],
        ['sub_device', 0, 255],
        ['function', 0, 255],
        ['extended_function', 0, 15]
    ]

    def _calc_checksum(self, function):
        f = self._invert_bits(function, 8)
        return f

    def decode(self, data, frequency=0):
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)
        if self._last_code is not None:
            if self._last_code == code:
                return self._last_code

            self._last_code.repeat_timer.stop()
            self._last_code = None

        checksum = self._calc_checksum(code.function)

        if checksum != code.checksum:
            raise DecodeError('Checksum failed')

        self._last_code = code
        return code

    def encode(self, device, sub_device, function, extended_function, repeat_count=0):
        checksum = self._calc_checksum(function)

        packet = self._build_packet(
            list(self._get_timing(device, i) for i in range(8)),
            list(self._get_timing(sub_device, i) for i in range(8)),
            self._middle_timings,
            list(self._get_timing(extended_function, i) for i in range(4)),
            list(self._get_timing(function, i) for i in range(8)),
            list(self._get_timing(checksum, i) for i in range(8))
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
            4500, -4500, 560, -560, 560, -560, 560, -1680, 560, -560, 560, -1680, 560, -560, 
            560, -1680, 560, -560, 560, -560, 560, -560, 560, -1680, 560, -560, 560, -560, 
            560, -560, 560, -1680, 560, -1680, 560, -5040, 560, -560, 560, -560, 560, -560, 
            560, -560, 560, -1680, 560, -560, 560, -560, 560, -1680, 560, -560, 560, -1680, 
            560, -560, 560, -1680, 560, -560, 560, -1680, 560, -1680, 560, -560, 560, -1680, 
            560, -560, 560, -1680, 560, -560, 560, -36840, 
        ]]

        params = [dict(function=169, sub_device=196, device=84, extended_function=0)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(function=169, sub_device=196, device=84, extended_function=0)
        protocol_base.IrProtocolBase._test_encode(self, params)


Samsung36 = Samsung36()
