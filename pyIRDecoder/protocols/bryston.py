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


class Bryston(protocol_base.IrProtocolBase):
    """
    IR decoder for the Bryston protocol.
    """
    irp = '{38.0k,315,lsb}<1,-6|6,-1>(D:10,F:8,-18m)*'
    frequency = 38000
    bit_count = 18
    encoding = 'lsb'

    _lead_out = [-18000]
    _bursts = [[TIMING, -TIMING * 6], [TIMING * 6, -TIMING]]

    _code_order = [
        ['D', 10],
        ['F', 8]
    ]

    _parameters = [
        ['D', 0, 9],
        ['F', 10, 17]
    ]
    # [D:0..1023,F:0..255]
    encode_parameters = [
        ['device', 0, 1023],
        ['function', 0, 255],
    ]

    def encode(
        self,
        device: int,
        function: int,
        repeat_count: int = 0
    ) -> protocol_base.IRCode:
        packet = self._build_packet(
            D=device,
            F=function,
        )

        params = dict(
            frequency=self.frequency,
            D=device,
            F=function,
        )

        code = protocol_base.IRCode(
            self,
            packet[:] * (repeat_count + 1),
            [packet[:]] * (repeat_count + 1),
            params,
            repeat_count
        )
        return code
