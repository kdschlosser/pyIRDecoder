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
    LeadInError,
    LeadOutError,
    TooManyBitsError,
    NotEnoughBitsError,
    IRStreamError
)

TIMING = 600


class DirecTV0(protocol_base.IrProtocolBase):
    """
    IR decoder for the DirecTV0 protocol.
    """
    irp = (
        '{40k,600,msb}<1,-1|1,-2|2,-1|2,-2>'
        '([10][5],-2,D:4,F:8,C:4,1,-15)'
        '{C=7*(F:2:6)+5*(F:2:4)+3*(F:2:2)+(F:2)}'
    )
    frequency = 40000
    bit_count = 16
    encoding = 'msb'

    _lead_in = []
    _lead_in1 = [TIMING * 10, -TIMING * 2]
    _lead_in2 = [TIMING * 5, -TIMING * 2]

    _lead_out = [TIMING, -TIMING * 15]
    _bursts = [
        [TIMING, -TIMING],
        [TIMING, -TIMING * 2],
        [TIMING * 2, -TIMING],
        [TIMING * 2, -TIMING * 2]
    ]

    _code_order = [
        ['D', 8],
        ['F', 8]
    ]
    _parameters = [
        ['D', 0, 3],
        ['F', 4, 11],
        ['CHECKSUM', 12, 15]
    ]
    # [D:0..15,F:0..255]
    encode_parameters = [
        ['device', 0, 15],
        ['function', 0, 255]
    ]

    _saved_code = None

    @staticmethod
    def _calc_checksum(
        function: protocol_base.IntegerWrapper
    ) -> protocol_base.IntegerWrapper:
        # {C=7*(F:2:6)+5*(F:2:4)+3*(F:2:2)+(F:2)}
        c = (
            7 * function[:2:6] +
            5 * function[:2:4] +
            3 * function[:2:2] +
            function[:2:0]
        )

        return c[:4:0]

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        cleaned_code = []
        original_code = data[:]
        code = data[:]

        if self._saved_code is None:
            self._lead_in = self._lead_in1[:]
        else:
            self._lead_in = self._lead_in2[:]

        try:
            mark, space = code[:2]
            code = code[2:]
        except ValueError:
            raise IRStreamError

        if (
            self._match(mark, self._lead_in[0]) and
            self._match(space, self._lead_in[1])
        ):
            cleaned_code += self._lead_in[:]
        else:
            raise LeadInError

        lead_out = code[-2:]
        code = code[:-2]

        for i, burst in enumerate(lead_out):
            e_burst = self._lead_out[i]

            if self._match(burst, e_burst):
                lead_out[i] = e_burst
            else:
                raise LeadOutError

        decoded = []
        for i in range(0, len(code), 2):
            mark = code[i]
            space = code[i + 1]

            for j, (e_mark, e_space) in enumerate(self._bursts):
                if self._match(mark, e_mark) and self._match(space, e_space):
                    cleaned_code += [e_mark, e_space]
                    decoded.extend([j >> 1 & 1, j & 1])
                    break
            else:
                raise IRStreamError

        if len(decoded) > self.bit_count:
            raise TooManyBitsError
        if len(decoded) < self.bit_count:
            raise NotEnoughBitsError

        cleaned_code += lead_out

        params = dict(frequency=self.frequency)

        for key, start_bit, stop_bit in self._parameters:
            value = 0
            for i in range(start_bit, stop_bit + 1):
                value |= decoded[i] << ~i + stop_bit + 1

            params[key] = protocol_base.IntegerWrapper(
                value,
                stop_bit + 1 - start_bit,
                self._bursts,
                self.encoding
            )

        checksum = self._calc_checksum(params['F'])

        if checksum != params['CHECKSUM']:
            raise DecodeError('Invalid checksum')

        normalized_code = []

        for pulse in cleaned_code:
            if (
                len(normalized_code) and
                (
                    normalized_code[-1] < 0 > pulse or
                    normalized_code[-1] > 0 < pulse
                )
            ):
                normalized_code[-1] += pulse
                continue

            normalized_code += [pulse]

        code = protocol_base.IRCode(
            self,
            original_code,
            normalized_code,
            params
        )

        if self._saved_code is None:
            self._saved_code = code
            raise RepeatLeadInError
        else:
            code = self._saved_code + code
            self._saved_code = None

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
            CHECKSUM=checksum
        )

        packet1 = self._lead_in1[:] + packet1

        packet2 = self._build_packet(
            D=device,
            F=function,
            CHECKSUM=checksum
        )

        packet2 = self._lead_in2[:] + packet2

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
