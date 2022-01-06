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


TIMING = 477


class Akord(protocol_base.IrProtocolBase):
    """
    IR decoder for the Akord protocol.
    """
    irp = (
        '{37.0k,477,msb}<1,-1|1,-2>(18,-8,D:8,S:8,F:8,~F:8,1,-40m,'
        '(18,-5,1,-78m)*)'
    )
    frequency = 37000
    bit_count = 32
    encoding = 'msb'

    _lead_in = [TIMING * 18, -TIMING * 8]
    _lead_out = [TIMING, -40000]
    _bursts = [[TIMING, -TIMING], [TIMING, -TIMING * 2]]

    _repeat_lead_in = [TIMING * 18, -TIMING * 5]
    _repeat_lead_out = [TIMING, -78000]

    _code_order = [
        ['D', 8],
        ['S', 8],
        ['F', 8]
    ]

    _parameters = [
        ['D', 0, 7],
        ['S', 8, 15],
        ['F', 16, 23],
        ['F_CHECKSUM', 24, 31]
    ]
    # [D:0..255,S:0..255,F:0..255]
    encode_parameters = [
        ['device', 0, 255],
        ['sub_device', 0, 255],
        ['function', 0, 255],
    ]

    @staticmethod
    def _calc_checksum(
        function: protocol_base.IntegerWrapper
    ) -> protocol_base.IntegerWrapper:
        f = function[True::]
        return f

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)
        if self._last_code is not None:
            if self._last_code == code:
                return self._last_code

            self._last_code.repeat_timer.stop()

        func_checksum = self._calc_checksum(code.function)

        if func_checksum != code.f_checksum:
            raise DecodeError('Checksum failed')

        self._last_code = code
        return code

    def encode(
        self,
        device: int,
        sub_device: int,
        function: int,
        repeat_count: int = 0
    ) -> protocol_base.IRCode:
        function = protocol_base.IntegerWrapper(
            function,
            8,
            self._bursts,
            self.encoding
        )

        func_checksum = self._calc_checksum(function)

        packet = self._build_packet(
            D=device,
            S=sub_device,
            F=function,
            F_CHECKSUM=func_checksum,
        )

        params = dict(
            frequency=self.frequency,
            D=device,
            S=sub_device,
            F=function
        )

        if repeat_count:
            repeat = self._repeat_lead_in[:] + self._repeat_lead_out[:]
            code = protocol_base.IRCode(
                self,
                packet[:] + (repeat[:] * repeat_count),
                [packet[:]] + ([repeat[:]] * repeat_count),
                params,
                repeat_count
            )

        else:
            code = protocol_base.IRCode(
                self,
                packet[:],
                [packet[:]],
                params,
                repeat_count
            )
        return code
