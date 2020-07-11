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


TIMING = 564


class Apple(protocol_base.IrProtocolBase):
    """
    IR decoder for the Apple protocol.
    """
    irp = (
        '{38.4k,564,lsb}<1,-1|1,-3>(16,-8,D:8,S:8,C:1,F:7,PairID:8,1,^108m,(16,-4,1,^108m)*)'
        '{C=1-(#F+#PairID)%2,S=135}'
    )
    frequency = 38400
    bit_count = 32
    encoding = 'lsb'

    _lead_in = [TIMING * 16, -TIMING * 8]
    _lead_out = [TIMING, 108000]
    _bursts = [[TIMING, -TIMING], [TIMING, -TIMING * 3]]

    _repeat_lead_in = [TIMING * 16, -TIMING * 4]
    _repeat_lead_out = [TIMING, 108000]

    _code_order = [
        ['D', 8],
        ['F', 7],
        ['PAIR_ID', 8]
    ]

    _parameters = [
        ['D', 0, 7],
        ['S', 8, 15],
        ['CHECKSUM', 16, 16],
        ['F', 17, 23],
        ['PAIR_ID', 24, 31]
    ]
    # [D:0..255=238,F:0..127,PairID:0..255]
    encode_parameters = [
        ['device', 0, 255],
        ['function', 0, 127],
        ['pair_id', 0, 255]
    ]

    def _calc_checksum(self, function, pair_id):
        c = 1 - (self._count_one_bits(function) + self._count_one_bits(pair_id)) % 2
        return c

    def decode(self, data, frequency=0):
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)

        if self._last_code is not None and self._last_code == code:
            return self.__last_code

        checksum = self._calc_checksum(code.function, code.pair_id)

        if code.sub_device != 135 or checksum != code.checksum:
            raise DecodeError('Checksum failed')

        return code

    def encode(self, device, function, pair_id, repeat_count=0):
        sub_device = 135
        checksum = self._calc_checksum(function, pair_id)

        packet = [
            self._build_packet(
                list(self._get_timing(device, i) for i in range(8)),
                list(self._get_timing(sub_device, i) for i in range(8)),
                list(self._get_timing(checksum, i) for i in range(1)),
                list(self._get_timing(function, i) for i in range(7)),
                list(self._get_timing(pair_id, i) for i in range(8))
            )
        ]

        params = dict(
            frequency=self.frequency,
            D=device,
            F=function,
            PAIR_ID=pair_id
        )

        code = protocol_base.IRCode(
            self,
            packet[:],
            packet[:] + self._build_repeat_packet(repeat_count),
            params,
            repeat_count
        )
        return code

    def _test_decode(self):
        rlc = [[
            9024, -4512, 564, -1692, 564, -564, 564, -1692, 564, -1692, 564, -564, 564, -1692, 564, -564,
            564, -564, 564, -1692, 564, -1692, 564, -1692, 564, -564, 564, -564, 564, -564, 564, -564,
            564, -1692, 564, -564, 564, -564, 564, -1692, 564, -564, 564, -1692, 564, -564, 564, -564,
            564, -564, 564, -1692, 564, -564, 564, -564, 564, -564, 564, -1692, 564, -1692, 564, -1692,
            564, -1692, 564, -40884
        ]]

        params = [dict(device=45, function=10, pair_id=241)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(device=45, function=10, pair_id=241)
        protocol_base.IrProtocolBase._test_encode(self, params)


Apple = Apple()

