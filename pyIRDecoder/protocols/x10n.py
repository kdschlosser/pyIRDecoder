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
    TooManyBitsError
)


TIMING = 565


class X10n(protocol_base.IrProtocolBase):
    """
    IR decoder for the X10.n protocol.
    """
    irp = '{40.8k,565,lsb}<2,-12|7,-7>(F:5,N:-4,21,-7,(7,-7,F:5,~F:5,21,-7)+)'
    frequency = 40800
    _bit_count1 = 9
    _bit_count2 = 10
    encoding = 'lsb'

    _lead_in = []
    _lead_out = [TIMING * 21, -TIMING * 7]
    _bursts = [[TIMING * 2, -TIMING * 12], [TIMING * 7, -TIMING * 7]]

    _repeat_lead_in = [TIMING * 7, -TIMING * 7]
    _repeat_lead_out = [TIMING * 21, -TIMING * 7]
    _middle_timings = []
    _repeat_bursts = []
    _has_repeat_lead_out = True

    _code_order = [
        ['F', 5],
        ['N', 4]
    ]

    _parameters1 = [
        ['F', 0, 4],
        ['N', 5, 8]
    ]
    _parameters2 = [
        ['F', 0, 4],
        ['CHECKSUM', 5, 9]
    ]

    # [F:0..31,N@:0..15=0]
    encode_parameters = [
        ['function', 0, 31],
        ['n', 0, 15]
    ]

    repeat_timeout = (TIMING * 14) * 13

    _first_code = None

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        self._lead_in = []
        self._parameters = self.__class__._parameters1
        self.bit_count = self.__class__._bit_count1
        try:
            code = protocol_base.IrProtocolBase.decode(self, data, frequency)
            self._first_code = code
            raise RepeatLeadInError
        except TooManyBitsError:
            self._lead_in = self.__class__._repeat_lead_in

            self._parameters = self.__class__._parameters2
            self.bit_count = self.__class__._bit_count2

            code = protocol_base.IrProtocolBase.decode(self, data, frequency)

        if self._first_code is None and self._last_code is None:
            raise DecodeError

        if code.function != self._first_code.function:
            self._first_code = None
            raise DecodeError('Invalid checksum')

        checksum = code.function[True:5:0]
        if checksum != code.checksum:
            raise DecodeError('Invalid checksum')

        if self._first_code is not None:
            self._first_code += code

            # noinspection PyProtectedMember
            self._first_code._data['CHECKSUM'] = code.checksum
            n = self._first_code.n[:-4:0]
            # noinspection PyProtectedMember
            self._first_code._data['N'] = n
            code = self._first_code
            self._first_code = None

        if self._last_code is not None:

            if self._last_code == code:
                return self._last_code

            self._last_code.repeat_timer.stop()

        self._last_code = code
        return code

    def encode(
        self,
        function: int,
        n: int,
        repeat_count: int = 0
    ) -> protocol_base.IRCode:
        function = protocol_base.IntegerWrapper(
            function,
            5,
            self._bursts,
            self.encoding
        )
        n_ = protocol_base.IntegerWrapper(
            n,
            4,
            self._bursts,
            self.encoding
        )[:-4:0]

        checksum = function[True:5:0]

        # (F:5,N:-4,21,-7,(7,-7,F:5,~F:5,21,-7)+)

        params1 = dict(
            F=function,
            N=n_
        )
        self.__class__._parameters = self.__class__._parameters1
        del self.__class__._lead_in[:]

        packet = self._build_packet(**params1)

        params2 = dict(
            F=function,
            CHECKSUM=checksum
        )
        self.__class__._parameters = self.__class__._parameters2
        self.__class__._lead_in = self.__class__._repeat_lead_in

        repeat = self._build_packet(**params2)

        params = dict(
            frequency=self.frequency,
            F=function,
            N=n,
            CHECKSUM=checksum
        )

        code = protocol_base.IRCode(
            self,
            packet[:] + (repeat[:] * (repeat_count + 1)),
            [packet[:]] + ([repeat[:]] * (repeat_count + 1)),
            params,
            repeat_count
        )

        return code

    def reset(self, code):
        protocol_base.IrProtocolBase.reset(self, code)
        self._first_code = None
