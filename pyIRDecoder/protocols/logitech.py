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
from . import DecodeError


TIMING = 127


class Logitech(protocol_base.IrProtocolBase):
    """
    IR decoder for the Logitech protocol.
    """
    irp = '{38k,127,lsb}<3,-4|3,-8>(31,-36,D:4,~D:4,F:8,~F:8,3,-50m)*'
    frequency = 38000
    bit_count = 24
    encoding = 'lsb'

    _lead_in = [TIMING * 31, -TIMING * 36]
    _lead_out = [TIMING * 3, -50000]
    _middle_timings = []
    _bursts = [[TIMING * 3, -TIMING * 4], [TIMING * 3, -TIMING * 8]]

    _code_order = [
        ['D', 4],
        ['F', 8],
    ]

    _parameters = [
        ['D', 0, 3],
        ['D_CHECKSUM', 4, 7],
        ['F', 8, 15],
        ['F_CHECKSUM', 16, 23],
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
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)
        dev_checksum, func_checksum = (
            self._calc_checksum(code.device, code.function)
        )

        if (
            dev_checksum != code.d_checksum or
            func_checksum != code.f_checksum
        ):
            raise DecodeError('Checksum failed')

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
            function
        )
        params = dict(
            D=device,
            F=function,
            D_CHECKSUM=dev_checksum,
            F_CHECKSUM=func_checksum
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
