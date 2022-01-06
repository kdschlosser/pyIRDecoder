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
    IRException,
    DecodeError,
    RepeatLeadInError,
    RepeatLeadOutError
)


TIMING = 500


class NRC16(protocol_base.IrProtocolBase):
    """
    IR decoder for the NRC16 protocol.
    """
    irp = (
        '{38k,500}<-1,1|1,-1>'
        '(1,-5,1:1,254:8,127:7,-15m,'
        '(1,-5,1:1,F:8,D:7,-110m)+,'
        '1,-5,1:1,254:8,127:7,-15m)'
    )
    frequency = 38000
    bit_count = 16
    encoding = 'lsb'

    _lead_in = [TIMING, -TIMING * 5]
    _lead_out = []
    _lead_out1 = [-15000]
    _lead_out2 = [-110000]
    _bursts = [[-TIMING, TIMING], [TIMING, -TIMING]]

    _has_repeat_lead_out = True

    _code_order = [
        ['F', 8],
        ['D', 7]
    ]

    _parameters = [
        ['C0', 0, 0],
        ['F', 1, 8],
        ['D', 9, 15]
    ]
    # [D:0..127,F:0..255]
    encode_parameters = [
        ['device', 0, 127],
        ['function', 0, 255],
    ]

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        self.__class__._lead_out = self._lead_out1[:]
        self._lead_out = self._lead_out1[:]

        try:
            code = protocol_base.IrProtocolBase.decode(self, data, frequency)
        except IRException:
            self.__class__._lead_out = self._lead_out2[:]
            self._lead_out = self._lead_out2[:]

            code = protocol_base.IrProtocolBase.decode(self, data, frequency)

        if code.c0 != 1:
            raise DecodeError('Invalid checksum')

        if self.__class__._lead_out == self._lead_out1:
            if (
                code.device != 127 or
                code.function != 254
            ):
                raise DecodeError('Invalid checksum')

            if self._last_code is None:
                raise RepeatLeadInError

            raise RepeatLeadOutError

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

        self.__class__._lead_out = self._lead_out1[:]
        prefix = suffix = self._build_packet(D=127, F=254, C0=1)

        self.__class__._lead_out = self._lead_out2[:]
        packet = self._build_packet(D=device, F=function, C0=1)

        params = dict(
            frequency=self.frequency,
            D=device,
            F=function,
            C0=1
        )

        code = protocol_base.IRCode(
            self,
            prefix[:] + (packet[:] * (repeat_count + 1)) + suffix[:],
            [prefix[:]] + ([packet[:]] * (repeat_count + 1)) + [suffix[:]],
            params,
            repeat_count
        )

        return code
