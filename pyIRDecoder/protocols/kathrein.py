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

from typing import Sequence

# Local imports
from . import protocol_base
from . import DecodeError, IRException


TIMING = 540


class Kathrein(protocol_base.IrProtocolBase):
    """
    IR decoder for the Kathrein protocol.
    """
    irp = (
        '{38k,540,lsb}<1,-1|1,-3>'
        '(16,-8,D:4,~D:4,F:8,~F:8,1,^105m,(16,-8,F:8,1,^105m)+)'
    )
    frequency = 38000
    bit_count = 24

    _bit_count1 = 24
    _bit_count2 = 8

    encoding = 'lsb'

    _lead_in = [TIMING * 16, -TIMING * 8]
    _lead_out = [TIMING, 105000]
    _middle_timings = []
    _bursts = [[TIMING, -TIMING], [TIMING, -TIMING * 3]]

    _code_order = [
        ['D', 4],
        ['F', 8]
    ]

    _parameters1 = [
        ['D', 0, 3],
        ['D_CHECKSUM', 4, 7],
        ['F', 8, 15],
        ['F_CHECKSUM', 16, 23],
    ]

    _parameters2 = [
        ['F', 0, 7],
    ]
    # [D:0..15,F:0..255]
    encode_parameters = [
        ['device', 0, 15],
        ['function', 0, 255],
    ]

    @staticmethod
    def _calc_checksum(
        device: protocol_base.IntegerWrapper,
        function: protocol_base.IntegerWrapper
    ) -> Sequence[protocol_base.IntegerWrapper]:
        d = device[True:4:0]
        f = function[True:8:0]
        return d, f

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        self.bit_count = self._bit_count1
        self._parameters = self._parameters1
        try:
            code = protocol_base.IrProtocolBase.decode(self, data, frequency)
            dev_checksum, func_checksum = (
                self._calc_checksum(code.device, code.function)
            )

            if (
                dev_checksum != code.d_checksum or
                func_checksum != code.f_checksum
            ):
                raise DecodeError('Checksum failed')
        except IRException:
            if self._last_code is None:
                raise

            self.bit_count = self._bit_count2
            self._parameters = self._parameters2
            try:
                code = (
                    protocol_base.IrProtocolBase.decode(self, data, frequency)
                )
            finally:
                self.bit_count = self._bit_count1
                self._parameters = self._parameters1

            if code.function != self._last_code.function:
                raise DecodeError

            return self._last_code

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
        self._parameters = self._parameters1

        device = protocol_base.IntegerWrapper(
            device,
            4,
            self._bursts,
            self.encoding
        )
        function = protocol_base.IntegerWrapper(
            function,
            8,
            self._bursts,
            self.encoding
        )
        dev_checksum, func_checksum = self._calc_checksum(
            device,
            function,
        )

        params = dict(
            D=device,
            F=function,
            D_CHECKSUM=dev_checksum,
            F_CHECKSUM=func_checksum
        )

        packet = self._build_packet(**params)
        repeat = self._build_packet(function.timings)

        params['frequency'] = self.frequency

        code = protocol_base.IRCode(
            self,
            packet[:] + (repeat * repeat_count),
            [packet[:]] + ([repeat] * repeat_count),
            params,
            repeat_count
        )

        return code
