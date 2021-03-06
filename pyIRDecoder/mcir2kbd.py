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

    def _calc_checksum(self, function, mode):
        # c1=#(F&0b11111000)%2,
        # c2=(#(F&0b00000111)+#(M&0b00110000))%2,
        # c3=(#(F&0b11000111)+#(M&0b10001110))%2,
        # c4=(#(F&0b00110110)+#(M&0b10101101))%2,
        # c5=(#(F&0b10101101)+#(M&0b10011011))%2,
        # C=(c1<<4)|(c2<<3)|(c3<<2)|(c4<<1)|c5}
        
        c1 = self._count_one_bits(function & 0b11111000) % 2
        c2 = (self._count_one_bits(function & 0b00000111) + self._count_one_bits(mode & 0b00110000)) % 2
        c3 = (self._count_one_bits(function & 0b11000111) + self._count_one_bits(mode & 0b10001110)) % 2
        c4 = (self._count_one_bits(function & 0b00110110) + self._count_one_bits(mode & 0b10101101)) % 2
        c5 = (self._count_one_bits(function & 0b10101101) + self._count_one_bits(mode & 0b10011011)) % 2

        c = (c1 << 4) | (c2 << 3) | (c3 << 2) | (c4 << 1) | c5

        return c

    def decode(self, data, frequency=0):
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)
        if self._last_code is not None:
            if self._last_code == code:
                return self._last_code

            self._last_code.repeat_timer.stop()
            self._last_code = None

        checksum = self._calc_checksum(code.function, code.mode)

        if checksum != code.checksum or code.c0 != 32 or code.c1 != 0:
            raise DecodeError('Checksum failed')

        self._last_code = code
        return code

    def encode(self, function, mode, repeat_count=0):
        c0 = 32
        c1 = 0

        checksum = self._calc_checksum(
            function,
            mode
        )

        packet = self._build_packet(
            list(self._get_timing(c0, i) for i in range(8)),
            list(self._get_timing(checksum, i) for i in range(5)),
            list(self._get_timing(c1, i) for i in range(8)),
            list(self._get_timing(function, i) for i in range(8)),
            list(self._get_timing(mode, i) for i in range(8)),
        )

        params = dict(
            frequency=self.frequency,
            M=mode,
            F=function,
        )

        code = protocol_base.IRCode(
            self,
            [packet[:]],
            [packet[:]] * (repeat_count + 1),
            params,
            repeat_count
        )

        return code

    def _test_decode(self):
        rlc = [[
            2700, -300, 300, -300, 600, -600, 300, -300, 300, -300, 300, -300, 300, -300, 
            300, -300, 600, -600, 300, -300, 600, -600, 300, -300, 300, -300, 300, -300, 300, -300, 
            300, -300, 300, -300, 300, -300, 600, -600, 600, -300, 300, -300, 300, -300, 300, -300, 
            300, -300, 300, -600, 300, -300, 600, -300, 300, -600, 300, -300, 300, -300, 
            600, -74300, 
        ]]

        params = [dict(function=191, mode=49)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(function=191, mode=49)
        protocol_base.IrProtocolBase._test_encode(self, params)


MCIR2kbd = MCIR2kbd()
