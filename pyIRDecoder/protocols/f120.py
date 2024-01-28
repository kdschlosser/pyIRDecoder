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
from . import (
    DecodeError, 
    IRException,
    LeadOutError,
    ExpectingMoreData
)

TIMING = 422


class F120(protocol_base.IrProtocolBase):
    """
    IR decoder for the F120 protocol.
    """
    irp = '{37.9k,422,lsb}<1,-3|3,-1>(D:3,H:1,F:8,-34,D:3,H:1,F:8){H=0}'
    frequency = 37900
    bit_count = 0
    _bit_count1 = 12
    _bit_count2 = 24
    encoding = 'lsb'

    _lead_in = []
    _lead_out = []
    _lead_out1 = [-TIMING * 34]
    _lead_out2 = []
    _middle_timings1 = []
    _middle_timings2 = [-TIMING * 34]
    _bursts = [[TIMING, -TIMING * 3], [TIMING * 3, -TIMING]]

    _repeat_lead_in = []
    _repeat_lead_out = []
    _repeat_bursts = []

    _code_order = [
        ['D', 3],
        ['F', 8],
    ]

    _parameters1 = [
        ['D', 0, 2],
        ['H', 3, 3],
        ['F', 4, 11]
    ]

    _parameters2 = [
        ['D', 0, 2],
        ['H', 3, 3],
        ['F', 4, 11],
        ['D1', 12, 14],
        ['H1', 15, 15],
        ['F1', 16, 23]
    ]
    # [D:0..7,F:0..255]
    encode_parameters = [
        ['device', 0, 7],
        ['function', 0, 255]
    ]

    _saved_code = None

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        self._lead_out = self._lead_out1
        self._middle_timings = self._middle_timings1
        self._parameters = self._parameters1
        self.bit_count = self._bit_count1

        try:
            code = protocol_base.IrProtocolBase.decode(self, data, frequency)

            if code.h != 0:
                raise DecodeError('Invalid checksum')
            
            self._saved_code = code
            raise ExpectingMoreData

        except LeadOutError:
            if self._saved_code is None:
                raise DecodeError

            self._lead_out = self._lead_out2
            try:
                code2 = (
                    protocol_base.IrProtocolBase.decode(self, data, frequency)
                )
                code1 = self._saved_code
                self._saved_code = None

                if code1 != code2:
                    raise DecodeError

                code = code1 + code2

            except IRException:
                self._middle_timings = self._middle_timings2
                self._parameters = self._parameters2
                self.bit_count = self._bit_count2
                code = (
                    protocol_base.IrProtocolBase.decode(self, data, frequency)
                )

                if (
                    code.device != code.d1 or
                    code.h != code.h1 or
                    code.function != code.f1
                ):
                    raise DecodeError('Invalid checksum')

        if self._last_code is not None:
            if self._last_code == code:
                return self._last_code

            self._last_code.repeat_timer.stop()

        if code.h != 0:
            raise DecodeError('Invalid checksum')

        self._last_code = code
        return code

    def encode(
        self, 
        device: int, 
        function: int, 
        repeat_count: int = 0
    ) -> protocol_base.IRCode:
        h = 0

        self._middle_timings = self._middle_timings1
        self._parameters = self._parameters1
        self._lead_out = self._lead_out1

        packet1 = self._build_packet(
            D=device,
            H=h,
            F=function,
        )
        packet2 = packet1[:]

        packet1[-1] += self._middle_timings2[0]

        params = dict(
            frequency=self.frequency,
            D=device,
            F=function,
        )

        code = protocol_base.IRCode(
            self,
            (packet1[:] + packet2[:]) * (repeat_count + 1),
            [packet1[:], packet2[:]] * (repeat_count + 1),
            params,
            repeat_count
        )

        return code
