# -*- coding: utf-8 -*-
#
# *****************************************************************************
# MIT License
#
# Copyright (c) 2020 Kevin G. Schlosser
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in 
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN 
# THE SOFTWARE.

# ****************************************************************************

# Local imports
from . import protocol_base


TIMING = 315


class TDC38(protocol_base.IrProtocolBase):
    """
    IR decoder for the TDC38 protocol.
    """
    irp = '{38k,315,msb}<-1,1|1,-1>(1,-1,D:5,S:5,F:7,-89m)*'
    frequency = 38000
    bit_count = 17
    encoding = 'msb'

    _lead_in = [TIMING, -TIMING]
    _lead_out = [-89000]
    _middle_timings = []
    _bursts = [[-TIMING, TIMING], [TIMING, -TIMING]]

    _code_order = [
        ['D', 5],
        ['S', 5],
        ['F', 7]
    ]

    _parameters = [
        ['D', 0, 4],
        ['S', 5, 9],
        ['F', 10, 16],
    ]
    # [D:0..31,S:0..31,F:0..127]
    encode_parameters = [
        ['device', 0, 31],
        ['sub_device', 0, 31],
        ['function', 0, 127],
    ]

    def encode(
        self,
        device: int,
        sub_device: int,
        function: int,
        repeat_count: int = 0
    ) -> protocol_base.IRCode:
        params = dict(
            D=device,
            S=sub_device,
            F=function,
        )

        packet = self._build_packet(**params)

        params['frequency'] = self.frequency

        code = protocol_base.IRCode(
            self,
            packet[:] * (repeat_count + 1),
            [packet[:]] * (repeat_count + 1),
            params,
            repeat_count
        )

        return code
