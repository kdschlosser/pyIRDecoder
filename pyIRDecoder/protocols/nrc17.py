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
    RepeatLeadInError,
    RepeatLeadOutError,
    IRException
)


TIMING = 500


class NRC17(protocol_base.IrProtocolBase):
    """
    IR decoder for the NRC17 protocol.
    """
    irp = (
        '{500,38k,25%}<-1,1|1,-1>'
        '(1,-5,1:1,254:8,255:8,-28, '
        '(1,-5,1:1,F:8,D:8,-220)*, '
        '1,-5,1:1,254:8,255:8,-200)'
    )
    frequency = 38000
    bit_count = 17
    encoding = 'lsb'

    _lead_in = [TIMING, -TIMING * 5]
    _lead_out = []
    _lead_out1 = [-TIMING * 28]
    _lead_out2 = [-TIMING * 220]
    _lead_out3 = [-TIMING * 200]
    _middle_timings = []
    _bursts = [[-TIMING, TIMING], [TIMING, -TIMING]]

    _has_repeat_lead_out = True

    _code_order = [
        ['F', 8],
        ['D', 8],
    ]

    _parameters = [
        ['C0', 0, 0],
        ['F', 1, 8],
        ['D', 9, 16]
    ]
    # [D:0..255,F:0..255]
    encode_parameters = [
        ['device', 0, 255],
        ['function', 0, 255],
    ]

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:

        tolerance = self.tolerance
        self.tolerance = 5
        lead_outs = (
            self._lead_out1[:], self._lead_out2[:], self._lead_out3[:]
        )
        for lead_out in lead_outs:
            self._lead_out = lead_out
            try:
                code = (
                    protocol_base.IrProtocolBase.decode(self, data, frequency)
                )
                break
            except IRException:
                continue
        else:
            self.tolerance = tolerance
            raise DecodeError('Invalid code')

        self.tolerance = tolerance

        if code.c0 != 1:
            raise DecodeError('Invalid checksum')

        if (
            self._lead_out == self._lead_out1 or
            self._lead_out == self._lead_out3
        ):
            if code.function != 254 or code.device != 255:
                raise DecodeError

            if self._lead_out == self._lead_out1:
                raise RepeatLeadInError

            if self._last_code is not None:
                self._last_code.repeat_timer.stop()
                self._last_code = None

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
    ):

        params = dict(
            D=255,
            F=254,
            C0=1
        )

        self.__class__._lead_out = self._lead_out1[:]
        prefix = self._build_packet(**params)

        self.__class__._lead_out = self._lead_out3[:]
        suffix = self._build_packet(**params)

        params['D'] = device
        params['F'] = function

        self.__class__._lead_out = self._lead_out2[:]
        packet = self._build_packet(**params)

        params['frequency'] = self.frequency

        code = protocol_base.IRCode(
            self,
            prefix[:] + (packet[:] * (repeat_count + 1)) + suffix[:],
            [prefix[:]] + ([packet[:]] * (repeat_count + 1)) + [suffix[:]],
            params,
            repeat_count
        )

        return code
