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
from . import DecodeError, RepeatLeadInError, NotEnoughBitsError

TIMING = 600


class SonyDSP(protocol_base.IrProtocolBase):
    """
    IR decoder for the SonyDSP protocol.
    """
    irp = (
        '{40k,600,lsb}<1,-1|2,-1>'
        '((4,-1,96:8,18:7,^45m)3,'
        '(4,-1,195:8,^45m),'
        '(4,-1,81:8,^45m),'
        '(4,-1,F:8,^45m),'
        '(4,-1,(F^145):8,11:7,^45m))'
    )
    frequency = 40000
    _bit_count1 = 15
    _bit_count2 = 8

    encoding = 'lsb'

    _lead_in = [TIMING * 4, -TIMING]
    _lead_out = [45000]
    _bursts = [[TIMING, -TIMING], [TIMING * 2, -TIMING]]
    _code_order = [
        ['F', 8]
    ]

    _parameters1 = [
        ['C0', 0, 7],
        ['C1', 8, 14]
    ]
    _parameters2 = [
        ['F', 0, 7]
    ]

    encode_parameters = [
        ['function', 0, 255]
    ]

    repeat_timeout = (
        ((TIMING * 3) * _bit_count1 * 4) +
        ((TIMING * 3) * _bit_count2 * 3) +
        (sum(abs(item) for item in _lead_in) * 7)
    )
    repeat_timeout += (_lead_out[0] * 7) - repeat_timeout

    _sequence = []

    @staticmethod
    def _calc_checksum(
        function: protocol_base.IntegerWrapper
    ) -> protocol_base.IntegerWrapper:
        return (function ^ 145)[:8:0]

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        self.bit_count = self.__class__._bit_count1
        self._parameters = self.__class__._parameters1

        try:
            code = protocol_base.IrProtocolBase.decode(self, data, frequency)

            if code.c1 == 18:
                if code.c0 != 96:
                    raise DecodeError

                self._sequence.append(code)
                raise RepeatLeadInError

            if (
                len(self._sequence) != 6 or
                not hasattr(self._sequence[-1], 'f')
            ):
                del self._sequence[:]
                raise DecodeError

            checksum = self._calc_checksum(self._sequence[-1].function)

            if code.c1 != 11 or code.c0 != checksum:
                del self._sequence[:]
                raise DecodeError

            code1, code2, code3, code4, code5, code6 = self._sequence
            del self._sequence[:]
            function = code6.function
            code = code1 + code2 + code3 + code4 + code5 + code6 + code
            # noinspection PyProtectedMember
            code._data['F'] = function
            # noinspection PyProtectedMember
            code._data['CHECKSUM'] = checksum

            if self._last_code is not None:
                if self._last_code == code:
                    return self._last_code

                self._last_code.refresh_timer.stop()
                self._last_code = None

            self._last_code = code
            return code

        except NotEnoughBitsError:
            self.bit_count = self.__class__._bit_count2
            self._parameters = self.__class__._parameters2
            code = protocol_base.IrProtocolBase.decode(self, data, frequency)

            if len(self._sequence) == 3:
                if code.function != 195:
                    del self._sequence[:]
                    raise DecodeError
            elif len(self._sequence) == 4:
                if code.function != 81:
                    del self._sequence[:]
                    raise DecodeError
            elif len(self._sequence) == 5:
                pass
            else:
                del self._sequence[:]
                raise DecodeError

            self._sequence.append(code)
            raise RepeatLeadInError

    def encode(
        self,
        function: int
    ) -> protocol_base.IRCode:
        function = protocol_base.IntegerWrapper(
            function,
            8,
            self._bursts,
            self.encoding
        )
        checksum = self._calc_checksum(function)

        params = dict(
            C0=96,
            C1=18
        )
        self.__class__._parameters = self.__class__._parameters1

        code1 = code2 = code3 = self._build_packet(**params)

        params = dict(
            C0=checksum,
            C1=11
        )
        code7 = self._build_packet(**params)

        self.__class__._parameters = self.__class__._parameters2

        params = dict(
            F=195
        )
        code4 = self._build_packet(**params)

        params = dict(
            F=81
        )
        code5 = self._build_packet(**params)
        params = dict(
            F=function
        )
        code6 = self._build_packet(**params)

        params['frequency'] = self.frequency

        o_packet = []
        n_packet = []
        for code in (code1, code2, code3, code4, code5, code6, code7):
            o_packet.extend(code[:])
            n_packet.append(code[:])

        code = protocol_base.IRCode(
            self,
            o_packet,
            n_packet,
            params
        )
        return code
