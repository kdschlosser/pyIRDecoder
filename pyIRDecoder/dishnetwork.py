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


TIMING = 406


class DishNetwork(protocol_base.IrProtocolBase):
    """
    IR decoder for the Dish_Network protocol.
    """
    irp = '{57.6k,406,lsb}<1,-7|1,-4>(1,-15,(F:-6,S:5,D:5,1,-15)+)'
    frequency = 57600
    bit_count = 16
    encoding = 'lsb'

    _lead_in = [TIMING, -TIMING * 15]
    _lead_out = [TIMING, -TIMING * 15]
    _middle_timings = []
    _bursts = [[TIMING, -TIMING * 7], [TIMING, -TIMING * 4]]

    _repeat_lead_in = [TIMING, -TIMING * 15]
    _repeat_lead_out = []
    _repeat_bursts = []

    _parameters = [
        ['F', 0, 5],
        ['S', 6, 10],
        ['D', 11, 15],
    ]
    # [F:0..63,S:0..31,D:0..31]
    encode_parameters = [
        ['device', 0, 31],
        ['sub_device', 0, 31],
        ['function', 0, 63]
    ]

    def decode(self, data, frequency=0):
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)
        function = self._reverse_bits(code.function, 6)

        params = dict(
            D=code.device,
            S=code.sub_device,
            F=function,
            frequency=self.frequency
        )

        return protocol_base.IRCode(
            self,
            code.original_rlc,
            code.normalized_rlc,
            params
        )

    def encode(self, device, sub_device, function):
        function = self._reverse_bits(function, 6)
        packet = self._build_packet(
            list(self._get_timing(function, i) for i in range(6)),
            list(self._get_timing(sub_device, i) for i in range(5)),
            list(self._get_timing(device, i) for i in range(5)),
        )

        return [packet]

    def _test_decode(self):
        rlc = [[
            406, -6090, 406, -1624, 406, -1624, 406, -1624, 406, -1624, 406, -1624, 406, -2842,
            406, -2842, 406, -1624, 406, -2842, 406, -1624, 406, -1624, 406, -1624, 406, -2842,
            406, -1624, 406, -2842, 406, -2842, 406, -6090,
        ]]

        params = [dict(device=5, function=62, sub_device=26)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(device=5, function=62, sub_device=26)
        protocol_base.IrProtocolBase._test_encode(self, params)


DishNetwork = DishNetwork()
