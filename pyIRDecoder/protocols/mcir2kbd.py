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


class MCIR2kbd(protocol_base.IrProtocolBase):
    """
    IR decoder for the MCIR2kbd protocol.
    """
    irp = (
        '{0k,300,msb}<-1,1|1,-1>(9,32:8,C:5,0:8,F:8,M:8,-74m)*'
        '{c1=#(F&0b11111000)%2,'
        'c2=(#(F&0b00000111)+#(M&0b00110000))%2,'
        'c3=(#(F&0b11000111)+#(M&0b10001110))%2,'
        'c4=(#(F&0b00110110)+#(M&0b10101101))%2,'
        'c5=(#(F&0b10101101)+#(M&0b10011011))%2,'
        'C=(c1<<4)|(c2<<3)|(c3<<2)|(c4<<1)|c5}'
    )
    frequency = 0
    bit_count = 37
    encoding = 'msb'

    _lead_in = [TIMING * 9]
    _lead_out = [-74000]
    _middle_timings = []
    _bursts = [[-TIMING, TIMING], [TIMING, -TIMING]]

    _code_order = [
        ['F', 8],
        ['M', 8]
    ]

    _parameters = [
        ['C0', 0, 7],
        ['CHECKSUM', 8, 12],
        ['C1', 13, 20],
        ['F', 21, 28],
        ['M', 29, 36]
    ]
    # [F:0..255,M:0..255]
    encode_parameters = [
        ['function', 0, 255],
        ['mode', 0, 255]
    ]

    @staticmethod
    def _calc_checksum(
        function: protocol_base.IntegerWrapper,
        mode: protocol_base.IntegerWrapper
    ) -> protocol_base.IntegerWrapper:
        # c1=#(F&248)%2,
        # c2=(#(F&7)+#(M&48))%2,
        # c3=(#(F&199)+#(M&142))%2,
        # c4=(#(F&54)+#(M&173))%2,
        # c5=(#(F&173)+#(M&155))%2,
        # C=(c1<<4)|(c2<<3)|(c3<<2)|(c4<<1)|c5}
        
        c1 = (function & 248).num_one_bits % 2
        c2 = ((function & 7).num_one_bits + (mode & 48).num_one_bits) % 2
        c3 = ((function & 199).num_one_bits + (mode & 142).num_one_bits) % 2
        c4 = ((function & 54).num_one_bits + (mode & 173).num_one_bits) % 2
        c5 = ((function & 173).num_one_bits + (mode & 155).num_one_bits) % 2

        c = (c1 << 4) | (c2 << 3) | (c3 << 2) | (c4 << 1) | c5
        return c[:5:0]

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)
        checksum = self._calc_checksum(code.function, code.mode)

        if checksum != code.checksum or code.c0 != 32 or code.c1 != 0:
            raise DecodeError(
                str(checksum) + ' : ' + str(code.checksum) + ' - ' +
                str(code.c0) + ': 32 - ' + str(code.c1) + ': 0'
            )
        if self._last_code is not None:
            if self._last_code == code:
                return self._last_code

            self._last_code.repeat_timer.stop()
            self._last_code = None

        self._last_code = code
        return code

    def encode(
        self,
        function: int,
        mode: int,
        repeat_count: int = 0
    ) -> protocol_base.IRCode:

        function = protocol_base.IntegerWrapper(
            function,
            8,
            self._bursts,
            self.encoding
        )
        mode = protocol_base.IntegerWrapper(
            mode,
            8,
            self._bursts,
            self.encoding
        )

        checksum = self._calc_checksum(
            function,
            mode
        )

        params = dict(
            M=mode,
            F=function,
            C0=32,
            C1=0,
            CHECKSUM=checksum
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
