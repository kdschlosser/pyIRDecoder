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


TIMING = 565


class X10(protocol_base.IrProtocolBase):
    """
    IR decoder for the X10 protocol.
    """
    irp = '{40.8k,565}<2,-12|7,-7>(7,-7,F:5,~F:5,21,-7)*'
    frequency = 40800

    bit_count = 10
    encoding = 'lsb'

    _lead_in = [TIMING * 7, -TIMING * 7]
    _lead_out = [TIMING * 21, -TIMING * 7]

    _bursts = [[TIMING * 2, -TIMING * 12], [TIMING * 7, -TIMING * 7]]

    _code_order = [
        ['F', 5]
    ]

    _parameters = [
        ['F', 0, 4],
        ['CHECKSUM', 5, 9]
    ]

    encode_parameters = [
        ['function', 0, 31],
    ]

    repeat_timeout = (TIMING * 14) * 13

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)
        checksum = code.function[True:5:0]

        if checksum != code.checksum:
            raise DecodeError('Invalid checksum')

        if self._last_code is not None:
            last_code = self._last_code
            if last_code == code:
                return last_code

            last_code.repeat_timer.stop()

        self._last_code = code
        return code

    def encode(
        self,
        function: int,
        repeat_count: int = 0
    ) -> protocol_base.IRCode:
        function = protocol_base.IntegerWrapper(
            function,
            5,
            self._bursts,
            self.encoding
        )
        checksum = function[True:5:0]
        params = dict(
            F=function,
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
