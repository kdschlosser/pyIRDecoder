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


TIMING = 320


class CanalSatLD(protocol_base.IrProtocolBase):
    """
    IR decoder for the CanalSatLD protocol.
    """
    irp = (
        '{56k,320,msb}<-1,1|1,-1>'
        '(T=0,(1,-1,D:7,S:6,T:1,0:1,F:6,~F:1,-85m,T=1)+)'
    )
    frequency = 56000
    bit_count = 22
    encoding = 'msb'

    _lead_in = [TIMING, -TIMING]
    _lead_out = [-85000]
    _bursts = [[-TIMING, TIMING], [TIMING, -TIMING]]

    _code_order = [
        ['D', 7],
        ['S', 6],
        ['F', 6]
    ]

    _parameters = [
        ['D', 0, 6],
        ['S', 7, 12],
        ['T', 13, 13],
        ['C0', 14, 14],
        ['F', 15, 20],
        ['F_CHECKSUM', 21, 21]
    ]
    # [D:0..127,S:0..63,F:0..63]
    encode_parameters = [
        ['device', 0, 127],
        ['sub_device', 0, 63],
        ['function', 0, 63],
    ]

    @staticmethod
    def _calc_checksum(
        function: protocol_base.IntegerWrapper
    ) -> protocol_base.IntegerWrapper:
        return function[True:1:0]

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)

        func_checksum = self._calc_checksum(code.function)

        if func_checksum != code.f_checksum or code.c0 != 0:
            raise DecodeError('Checksum failed')

        if self._last_code is not None:
            if (
                self._last_code == code and
                code.toggle == 1
            ):
                return self._last_code

            self._last_code.repeat_timer.stop()

        if code.toggle == 0:
            # noinspection PyProtectedMember
            code._data['T'] = 1
            self._last_code = code
        else:
            raise DecodeError('toggle bit incorrect')

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
            6,
            self._bursts,
            self.encoding
        )

        checksum = self._calc_checksum(function)

        lead_in = self._build_packet(
            D=device,
            S=sub_device,
            T=0,
            C0=0,
            F=function,
            F_CHECKSUM=checksum
        )

        packet = self._build_packet(
            D=device,
            S=sub_device,
            T=1,
            C0=0,
            F=function,
            F_CHECKSUM=checksum
        )

        params = dict(
            frequency=self.frequency,
            D=device,
            S=sub_device,
            F=function
        )

        code = protocol_base.IRCode(
            self,
            lead_in[:] + (packet * (repeat_count + 1)),
            [lead_in[:]] + ([packet] * (repeat_count + 1)),
            params,
            repeat_count
        )
        return code
