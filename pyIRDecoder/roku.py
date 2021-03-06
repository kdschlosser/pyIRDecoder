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
from . import DecodeError, RepeatLeadIn


TIMING = 564


class Roku(protocol_base.IrProtocolBase):
    """
    IR decoder for the Roku protocol.
    """
    irp = '{38.0k,564,lsb}<1,-1|1,-3>(16,-8,D:8,S:8,F:7,0:1,~F:7,1:1,1,^108m,(16,-8,D:8,S:8,F:7,1:1,~F:7,0:1,1,^108m)*)'
    frequency = 38000
    bit_count = 32
    encoding = 'lsb'

    _lead_in = [TIMING * 16, -TIMING * 8]
    _lead_out = [TIMING, 108000]
    _middle_timings = []
    _bursts = [[TIMING, -TIMING], [TIMING, -TIMING * 3]]

    _code_order = [
        ['D', 8],
        ['S', 8],
        ['F', 7],
    ]

    _parameters = [
        ['D', 0, 7],
        ['S', 8, 15],
        ['F', 16, 22],
        ['T', 23, 23],
        ['F_CHECKSUM', 24, 30],
        ['T1', 31, 31]
    ]
    # [D:0..255,S:0..255=255-D,F:0..127]
    encode_parameters = [
        ['device', 0, 255],
        ['sub_device', 0, 255],
        ['function', 0, 127],
    ]

    def __init__(self, parent=None, xml=None):
        protocol_base.IrProtocolBase.__init__(self, parent, xml)
        if xml is None:
            self._enabled = False

    def _calc_checksum(self, function):
        f = self._invert_bits(function, 7)
        return f

    def decode(self, data, frequency=0):
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)

        if self._last_code is not None:
            if self._last_code != code:
                pass
            elif (
                self._last_code.toggle == code.toggle or
                (self._last_code.toggle == code.t1 and self._last_code.t1 == code.toggle)
            ):
                return self._last_code

            self._last_code.repeat_timer.stop()

        func_checksum = self._calc_checksum(code.function)

        if func_checksum != code.f_checksum:
            raise DecodeError('Checksum failed')

        self._last_code = code

        if not code.toggle:
            raise RepeatLeadIn

        return code

    def encode(self, device, sub_device, function, repeat_count=0):
        toggle1 = 0
        toggle2 = 1
        func_checksum = self._calc_checksum(function)

        code = self._build_packet(
            list(self._get_timing(device, i) for i in range(8)),
            list(self._get_timing(sub_device, i) for i in range(8)),
            list(self._get_timing(function, i) for i in range(7)),
            list(self._get_timing(toggle1, i) for i in range(1)),
            list(self._get_timing(func_checksum, i) for i in range(7)),
            list(self._get_timing(toggle2, i) for i in range(1)),
        )

        repeat = self._build_packet(
            list(self._get_timing(device, i) for i in range(8)),
            list(self._get_timing(sub_device, i) for i in range(8)),
            list(self._get_timing(function, i) for i in range(7)),
            list(self._get_timing(toggle2, i) for i in range(1)),
            list(self._get_timing(func_checksum, i) for i in range(7)),
            list(self._get_timing(toggle1, i) for i in range(1)),
        )

        packet = [code]
        packet += [repeat] * (repeat_count + 1)

        params = dict(
            frequency=self.frequency,
            D=device,
            S=sub_device,
            F=function,
        )

        code = protocol_base.IRCode(
            self,
            [code[:], repeat[:]],
            packet[:],
            params,
            repeat_count
        )

        return code

    def _test_decode(self):
        rlc = [
            [
                +9024, -4512, +564, -564, +564, -1692, +564, -564, +564, -1692, +564, -564, +564, -564, +564, -564,
                +564, -1692, +564, -1692, +564, -1692, +564, -1692, +564, -1692, +564, -564, +564, -564, +564, -1692,
                +564, -1692, +564, -1692, +564, -564, +564, -1692, +564, -564, +564, -1692, +564, -564, +564, -1692,
                +564, -564, +564, -564, +564, -1692, +564, -564, +564, -1692, +564, -564, +564, -1692, +564, -564,
                +564, -1692, +564, -38628
            ],
            [
                +9024, -4512, +564, -564, +564, -1692, +564, -564, +564, -1692, +564, -564, +564, -564, +564, -564,
                +564, -1692, +564, -1692, +564, -1692, +564, -1692, +564, -1692, +564, -564, +564, -564, +564, -1692,
                +564, -1692, +564, -1692, +564, -564, +564, -1692, +564, -564, +564, -1692, +564, -564, +564, -1692,
                +564, -1692, +564, -564, +564, -1692, +564, -564, +564, -1692, +564, -564, +564, -1692, +564, -564,
                +564, -564, +564, -38628
            ]
        ]

        params = [
            None,
            dict(device=138, function=85, sub_device=207)
        ]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(device=19, function=105, sub_device=17)
        protocol_base.IrProtocolBase._test_encode(self, params)


Roku = Roku()
