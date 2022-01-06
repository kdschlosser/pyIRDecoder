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
from . import DecodeError


TIMING = 300


class MCIR2mouse(protocol_base.IrProtocolBase):
    """
    IR decoder for the MCIR2mouse protocol.
    """
    irp = '{0k,300,msb}<-1,1|1,-1>(9,8:8,C:5,y:7,x:7,R:1,L:1,F:5,-10.7m)*'
    frequency = 0
    bit_count = 34
    encoding = 'msb'

    _lead_in = [TIMING * 9]
    _lead_out = [-10700]
    _middle_timings = []
    _bursts = [[-TIMING, TIMING], [TIMING, -TIMING]]

    _code_order = [
        ['MIDDLE', 5],
        ['Y', 7],
        ['X', 7],
        ['RIGHT', 1],
        ['LEFT', 1],
        ['F', 5]
    ]

    _parameters = [
        ['C0', 0, 7],
        ['MIDDLE', 8, 12],
        ['Y', 13, 19],
        ['X', 20, 26],
        ['RIGHT', 27, 27],
        ['LEFT', 28, 28],
        ['F', 29, 33]
    ]
    # [C:0..31,L:0..1,R:0..1,x:0..127,y:0..127,F:0..31]
    encode_parameters = [
        ['middle', 0, 31],
        ['left', 0, 1],
        ['right', 0, 1],
        ['x', 0, 127],
        ['y', 0, 127],
        ['function', 0, 31]

    ]

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)

        if code.c0 != 8:
            raise DecodeError('Checksum failed')

        return code

    def encode(
        self,
        middle: int,
        left: int,
        right: int,
        x: int,
        y: int,
        function: int,
        repeat_count: int = 0
    ) -> protocol_base.IRCode:

        params = dict(
            MIDDLE=middle,
            X=x,
            Y=y,
            RIGHT=right,
            LEFT=left,
            F=function,
            C0=8
        )

        packet = self._build_packet(**params)

        params['frequency'] = self.frequency

        code = protocol_base.IRCode(
            self,
            packet[:],
            [packet[:]],
            params,
            0
        )

        return code
