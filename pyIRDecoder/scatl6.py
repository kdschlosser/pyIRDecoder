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


TIMING = 846


class ScAtl6(protocol_base.IrProtocolBase):
    """
    IR decoder for the ScAtl6 protocol.
    """
    irp = '{57.6k,846,lsb}<1,-1|1,-3>(4,-4,D:6,F:6,~D:6,~F:6,1,-40)*'
    frequency = 57600
    bit_count = 24
    encoding = 'lsb'

    _lead_in = [TIMING * 4, -TIMING * 4]
    _lead_out = [TIMING, -TIMING * 40]
    _middle_timings = []
    _bursts = [[TIMING, -TIMING], [TIMING, -TIMING * 3]]

    _repeat_lead_in = []
    _repeat_lead_out = []
    _repeat_bursts = []

    _parameters = [
        ['D', 0, 5],
        ['F', 6, 11],
        ['D_CHECKSUM', 12, 17],
        ['F_CHECKSUM', 18, 23],
    ]
    # [D:0..63,F:0..63]
    encode_parameters = [
        ['device', 0, 63],
        ['function', 0, 63],
    ]

    def _calc_checksum(self, device, function):
        f = self._invert_bits(function, 6)
        d = self._invert_bits(device, 6)
        return d, f

    def decode(self, data, frequency=0):
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)
        dev_checksum, func_checksum = self._calc_checksum(code.device, code.function)

        if dev_checksum != code.d_checksum or func_checksum != code.f_checksum:
            raise DecodeError('Checksum failed')

        return code

    def encode(self, device, function):
        dev_checksum, func_checksum = self._calc_checksum(
            device,
            function,
        )

        packet = self._build_packet(
            list(self._get_timing(device, i) for i in range(6)),
            list(self._get_timing(function, i) for i in range(6)),
            list(self._get_timing(dev_checksum, i) for i in range(6)),
            list(self._get_timing(func_checksum, i) for i in range(6))
        )

        return [packet]

    def _test_decode(self):
        rlc = [[
            3384, -3384, 846, -2538, 846, -2538, 846, -2538, 846, -2538, 846, -2538, 846, -846, 
            846, -846, 846, -2538, 846, -846, 846, -2538, 846, -846, 846, -2538, 846, -846, 
            846, -846, 846, -846, 846, -846, 846, -846, 846, -2538, 846, -2538, 846, -846, 
            846, -2538, 846, -846, 846, -2538, 846, -846, 846, -33840, 
        ]]

        params = [dict(device=31, function=42)]

        protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(device=31, function=42)
        protocol_base.IrProtocolBase._test_encode(self, params)


ScAtl6 = ScAtl6()
