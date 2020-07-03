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


TIMING = 182


class GuangZhou(protocol_base.IrProtocolBase):
    """
    IR decoder for the GuangZhou protocol.
    """
    irp = '{38.0k,182,lsb}<3,-3|3,-6>(20,-10,T:2,D:6,F:8,S:8,20,-10,~T:2,D:6,~F:8,3,^108m,(20,-20,3,^108m)*){T=3}'
    frequency = 38000
    bit_count = 40
    encoding = 'lsb'

    _lead_in = [TIMING * 20, -TIMING * 10]
    _lead_out = [TIMING * 3, 108000]
    _middle_timings = [(TIMING * 20, -TIMING * 10)]
    _bursts = [[TIMING * 3, -TIMING * 3], [TIMING * 3, -TIMING * 6]]

    _repeat_lead_in = [TIMING * 20, -TIMING * 20]
    _repeat_lead_out = [TIMING * 3, 108000]
    _repeat_bursts = []
# T:2,D:6,F:8,S:8,20,-10,~T:2,D:6,~F:8
    _parameters = [
        ['T', 0, 1],
        ['D', 2, 7],
        ['F', 8, 15],
        ['S', 16, 23],
        ['T_CHECKSUM', 24, 25],
        ['D_CHECKSUM', 26, 31],
        ['F_CHECKSUM', 32, 39]

    ]
    # [D:0..63,F:0..255,S:0..255]
    encode_parameters = [
        ['device', 0, 63],
        ['sub_device', 0, 255],
        ['function', 0, 255],
    ]

    def _calc_checksum(self, device, function, toggle):
        f = self._invert_bits(function, 8)
        t = self._invert_bits(toggle, 2)
        return device, f, t

    def decode(self, data, frequency=0):
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)
        dev_checksum, func_checksum, toggle_checksum = self._calc_checksum(code.device, code.function, code.toggle)

        if dev_checksum != code.d_checksum or func_checksum != code.f_checksum or toggle_checksum != code.t_checksum:
            raise DecodeError('Checksum failed')

        return code

    def encode(self, device, sub_device, function):
        toggle = 3

        dev_checksum, func_checksum, toggle_checksum = self._calc_checksum(device, function, toggle)

        packet = self._build_packet(
            list(self._get_timing(toggle, i) for i in range(2)),
            list(self._get_timing(device, i) for i in range(6)),
            list(self._get_timing(function, i) for i in range(8)),
            list(self._get_timing(sub_device, i) for i in range(8)),
            self._middle_timings[0],
            list(self._get_timing(toggle_checksum, i) for i in range(2)),
            list(self._get_timing(dev_checksum, i) for i in range(6)),
            list(self._get_timing(func_checksum, i) for i in range(8)),
        )

        return [packet]

    def _test_decode(self):
        rlc = [
            [
                +3640, -1820, +546, -1092, +546, -1092, +546, -546, +546, -546, +546, -1092, +546, -546, +546, -1092,
                +546, -546, +546, -546, +546, -546, +546, -1092, +546, -546, +546, -546, +546, -546, +546, -546, +546,
                -546, +546, -546, +546, -1092, +546, -1092, +546, -546, +546, -546, +546, -1092, +546, -1092, +546,
                -546, +3640, -1820, +546, -546, +546, -546, +546, -546, +546, -546, +546, -1092, +546, -546, +546,
                -1092, +546, -546, +546, -1092, +546, -1092, +546, -546, +546, -1092, +546, -1092, +546, -1092, +546,
                -1092, +546, -1092, +546, -43026
            ]
        ]
        params = [dict(device=20, function=4, sub_device=102)]

        protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(device=20, function=4, sub_device=102)
        protocol_base.IrProtocolBase._test_encode(self, params)


GuangZhou = GuangZhou()
