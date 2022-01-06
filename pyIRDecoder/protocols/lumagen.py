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


TIMING = 416


class Lumagen(protocol_base.IrProtocolBase):
    """
    IR decoder for the Lumagen protocol.
    """
    irp = (
        '{38.4k,416,msb}<1,-6|1,-12>'
        '(D:4,C:1,F:7,1,-26)*'
        '{C=(#F+1)&1}'
    )
    frequency = 38400
    bit_count = 12
    encoding = 'msb'

    _lead_in = []
    _lead_out = [TIMING, -TIMING * 26]
    _middle_timings = []
    _bursts = [[TIMING, -TIMING * 6], [TIMING, -TIMING * 12]]

    _repeat_lead_in = [TIMING * 16, -TIMING * 8]
    _repeat_lead_out = [TIMING, 108000]

    _code_order = [
        ['D', 4],
        ['F', 7],
    ]

    _parameters = [
        ['D', 0, 3],
        ['CHECKSUM', 4, 4],
        ['F', 5, 11],
    ]
    # [D:0..15,F:0..127]
    encode_parameters = [
        ['device', 0, 15],
        ['function', 0, 127],
    ]

    @classmethod
    def _calc_checksum(
        cls,
        function: protocol_base.IntegerWrapper
    ) -> protocol_base.IntegerWrapper:
        return (function.num_one_bits + 1 & 1)[:1:0]

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)

        checksum = self._calc_checksum(code.function)

        if checksum != code.checksum:
            raise DecodeError(str(checksum) + ' : ' + str(code.checksum))

        if self._last_code is not None:
            if self._last_code == code:
                return self._last_code

            self._last_code.repeat_timer.stop()
            self._last_code = None

        self._last_code = code
        return code

    def encode(
        self,
        device: int,
        function: int,
        repeat_count: int = 0
    ) -> protocol_base.IRCode:
        function = protocol_base.IntegerWrapper(
            function,
            7,
            self._bursts,
            self.encoding
        )

        checksum = self._calc_checksum(function)
        params = dict(
            D=device,
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
