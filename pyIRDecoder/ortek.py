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


class Ortek(protocol_base.IrProtocolBase):
    """
    IR decoder for the Ortek protocol.
    """
    irp = '{40.0k,564,lsb}<1,-1|1,-3>(16,-8,D:8,S:8,F:8,F:4:4,~F:4,1,^108m,(16,-4,1,-3,1,^108m)*)'
    frequency = 40000
    bit_count = 32
    encoding = 'lsb'

    _lead_in = [TIMING * 16, -TIMING * 8]
    _lead_out = [TIMING, 108000]
    _middle_timings = []
    _bursts = [[TIMING, -TIMING], [TIMING, -TIMING * 3]]

    _repeat_lead_in = [TIMING * 16, -TIMING * 4]
    _repeat_lead_out = [TIMING, 108000]
    _repeat_bursts = [[TIMING, -TIMING * 3]]

    _parameters = [
        ['D', 0, 7],
        ['S', 8, 15],
        ['F', 16, 23],
        ['CHECKSUM1', 24, 27],
        ['CHECKSUM2', 28, 31]
    ]
    # [D:0..255,S:0..255,F:0..255]
    encode_parameters = [
        ['device', 0, 255],
        ['sub_device', 0, 255],
        ['function', 0, 255],
    ]

    def _calc_checksum(self, function):
        f1 = self._get_bits(function, 4, 7)
        f2 = self._get_bits(function, 0, 3)
        f2 = self._invert_bits(f2, 4)

        return f1, f2

    def decode(self, data, frequency=0):
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)
        checksum1, checksum2 = self._calc_checksum(code.function)

        if checksum1 != code.checksum1 or checksum2 != code.checksum2:
            raise DecodeError('Checksum failed')

        return code

    def encode(self, device, sub_device, function):
        checksum1, checksum2 = self._calc_checksum(function)

        packet = self._build_packet(
            list(self._get_timing(device, i) for i in range(8)),
            list(self._get_timing(sub_device, i) for i in range(8)),
            list(self._get_timing(function, i) for i in range(8)),
            list(self._get_timing(checksum1, i) for i in range(4)),
            list(self._get_timing(checksum2, i) for i in range(4))
        )

        return [packet]

    def _test_decode(self):
        rlc = [[
            9024, -4512, 564, -1692, 564, -564, 564, -1692, 564, -1692, 564, -1692, 564, -564, 
            564, -1692, 564, -564, 564, -564, 564, -564, 564, -564, 564, -564, 564, -1692, 
            564, -564, 564, -1692, 564, -1692, 564, -564, 564, -564, 564, -564, 564, -564, 
            564, -1692, 564, -564, 564, -564, 564, -564, 564, -1692, 564, -564, 564, -564, 
            564, -564, 564, -1692, 564, -1692, 564, -1692, 564, -1692, 564, -42012, 
        ]]

        params = [dict(device=93, function=16, sub_device=208)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(device=93, function=16, sub_device=208)
        protocol_base.IrProtocolBase._test_encode(self, params)


Ortek = Ortek()
