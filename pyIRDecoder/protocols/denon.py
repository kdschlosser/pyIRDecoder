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
from . import DecodeError, IRException, RepeatLeadInError

TIMING = 264


class Denon(protocol_base.IrProtocolBase):
    """
    IR decoder for the Denon protocol.
    """
    irp = '{38k,264,lsb}<1,-3|1,-7>(D:5,F:8,0:2,1,-165,D:5,~F:8,3:2,1,-165)*'
    frequency = 38000
    bit_count = 0
    _bit_count1 = 15
    _bit_count2 = 30
    encoding = 'lsb'

    _lead_out = [TIMING, -TIMING * 165]
    _middle_timings1 = []
    _middle_timings2 = [(TIMING, -TIMING * 165)]
    _bursts = [[TIMING, -TIMING * 3], [TIMING, -TIMING * 7]]

    repeat_timeout = (
        sum(abs(item) for item in _lead_out) +
        (sum(abs(item) for item in _bursts[1]) * _bit_count2)
    ) * 2

    _code_order = [
        ['D', 5],
        ['F', 8]
    ]

    _parameters1 = [
        ['D', 0, 4],
        ['F', 5, 12],
        ['C0', 13, 14]
    ]
    _parameters2 = [
        ['D', 0, 4],
        ['F', 5, 12],
        ['C0', 13, 14],
        ['D_CHECKSUM', 15, 19],
        ['F_CHECKSUM', 20, 27],
        ['C1', 28, 29]
    ]

    # [D:0..31,F:0..255]
    encode_parameters = [
        ['device', 0, 31],
        ['function', 0, 255],
    ]

    @staticmethod
    def _calc_checksum(
        function: protocol_base.IntegerWrapper
    ) -> protocol_base.IntegerWrapper:
        return function[True:8:0]

    _sequence_code = None

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        self.bit_count = self._bit_count2
        self._parameters = self._parameters2
        self._middle_timings = self._middle_timings2[:]
        try:
            code = protocol_base.IrProtocolBase.decode(self, data, frequency)
            self._sequence_code = None

            func_checksum = self._calc_checksum(code.function)

            if (
                code.c0 != 0 or
                code.c1 != 3 or
                code.device != code.d_checksum or
                func_checksum != code.f_checksum
            ):
                raise DecodeError('invalid checksum')

        except IRException:
            self.bit_count = self._bit_count1
            self._parameters = self._parameters1
            self._middle_timings = self._middle_timings1[:]

            code = protocol_base.IrProtocolBase.decode(self, data, frequency)
            if self._sequence_code is None:
                self._sequence_code = code
                raise RepeatLeadInError

            c0 = self._sequence_code.c0
            c1 = code.c0
            device = self._sequence_code.device
            d_checksum = code.device
            function = self._sequence_code.function
            f_checksum = code.function
            func_checksum = self._calc_checksum(function)

            if (
                c0 != 0 or
                c1 != 3 or
                device != d_checksum or
                func_checksum != f_checksum
            ):
                self._sequence_code = None
                raise DecodeError('invalid checksum')

            original_rlc = self._sequence_code.original_rlc
            normalized_rlc = self._sequence_code.normalized_rlc
            original_rlc += code.original_rlc
            normalized_rlc += code.normalized_rlc

            params = dict(
                frequency=self.frequency,
                D=device,
                F=function,
                D_CHECKSUM=d_checksum,
                F_CHECKSUM=f_checksum,
                C0=c0,
                C1=c1
            )
            code = protocol_base.IRCode(
                self,
                original_rlc,
                normalized_rlc,
                params
            )

        if self._last_code is not None:
            if self._last_code == code:
                return self._last_code

            self._last_code.repeat_timer.stop()

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
            8,
            self._bursts,
            self.encoding
        )
        checksum = self._calc_checksum(function)

        packet1 = self._build_packet(
            D=device,
            F=function,
            C0=0,
        )
        packet2 = self._build_packet(
            D_CHECKSUM=device,
            F_CHECKSUM=checksum,
            C1=3,
        )

        params = dict(
            frequency=self.frequency,
            D=device,
            F=function
        )

        code = protocol_base.IRCode(
            self,
            (packet1[:] + packet2[:]) * (repeat_count + 1),
            [packet1[:] + packet2[:]] * (repeat_count + 1),
            params,
            repeat_count
        )

        return code
