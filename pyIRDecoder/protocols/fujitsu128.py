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

TIMING = 413


class Fujitsu128(protocol_base.IrProtocolBase):
    """
    IR decoder for the Fujitsu128 protocol.
    """
    irp = (
        '{38.4k,413,lsb}<1,-1|1,-3>'
        '(8,-4,A0:8,A1:8,A2:8,A3:8,A4:8,A5:8,A6:8,A7:8,A8:8,'
        'A9:8,A10:8,A11:8,A12:8,A13:8,A14:8,A15:8,1,-104.3m)*'
    )
    frequency = 38400
    bit_count = 128
    encoding = 'lsb'

    _lead_in = [TIMING * 8, -TIMING * 4]
    _lead_out = [TIMING, -104300]
    _middle_timings = []
    _bursts = [[TIMING, -TIMING], [TIMING, -TIMING * 3]]

    _code_order = [
        ['A0', 8],
        ['A1', 8],
        ['A2', 8],
        ['A3', 8],
        ['A4', 8],
        ['A5', 8],
        ['A6', 8],
        ['A7', 8],
        ['A8', 8],
        ['A9', 8],
        ['A10', 8],
        ['A11', 8],
        ['A12', 8],
        ['A13', 8],
        ['A14', 8],
        ['A15', 8],
    ]

    _parameters = [
        ['A0', 0, 7],
        ['A1', 8, 15],
        ['A2', 16, 23],
        ['A3', 24, 31],
        ['A4', 32, 39],
        ['A5', 40, 47],
        ['A6', 48, 55],
        ['A7', 56, 63],
        ['A8', 64, 71],
        ['A9', 72, 79],
        ['A10', 80, 87],
        ['A11', 88, 95],
        ['A12', 96, 103],
        ['A13', 104, 111],
        ['A14', 112, 119],
        ['A15', 120, 127],
    ]
    # [
    # A0:0..255,
    # A1:0..255,
    # A2:0..255,
    # A3:0..255,
    # A4:0..255,
    # A5:0..255,
    # A6:0..255,
    # A7:0..255,
    # A8:0..255,
    # A9:0..255,
    # A10:0..255,
    # A11:0..255,
    # A12:0..255,
    # A13:0..255,
    # A14:0..255,
    # A15:0..255
    # ]
    encode_parameters = [
        ['a0', 0, 255],
        ['a1', 0, 255],
        ['a2', 0, 255],
        ['a3', 0, 255],
        ['a4', 0, 255],
        ['a5', 0, 255],
        ['a6', 0, 255],
        ['a7', 0, 255],
        ['a8', 0, 255],
        ['a9', 0, 255],
        ['a10', 0, 255],
        ['a11', 0, 255],
        ['a12', 0, 255],
        ['a13', 0, 255],
        ['a14', 0, 255],
        ['a15', 0, 255],
    ]

    def encode(
        self,
        a0: int,
        a1: int,
        a2: int,
        a3: int,
        a4: int,
        a5: int,
        a6: int,
        a7: int,
        a8: int,
        a9: int,
        a10: int,
        a11: int,
        a12: int,
        a13: int,
        a14: int,
        a15: int,
        repeat_count: int = 0
    ) -> protocol_base.IRCode:
        params = dict(
            A0=a0,
            A1=a1,
            A2=a2,
            A3=a3,
            A4=a4,
            A5=a5,
            A6=a6,
            A7=a7,
            A8=a8,
            A9=a9,
            A10=a10,
            A11=a11,
            A12=a12,
            A13=a13,
            A14=a14,
            A15=a15
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
