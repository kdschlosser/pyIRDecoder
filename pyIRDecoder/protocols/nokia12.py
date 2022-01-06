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
    IRStreamError,
    LeadInError,
    LeadOutError,
    TooManyBitsError,
    NotEnoughBitsError
)


TIMING = 27.77777777777778


class Nokia12(protocol_base.IrProtocolBase):
    """
    IR decoder for the Nokia12 protocol.
    """
    irp = (
        '{36k,27.77777777777778,msb}<6,-10|6,-16|6,-22|6,-28>'
        '(15,-10,D:4,F:8,6,^100m)*'
    )
    frequency = 36000
    bit_count = 12
    encoding = 'msb'

    _lead_in = [int(TIMING * 15), int(-TIMING * 10)]
    _lead_out = [int(TIMING * 6), 100000]
    _bursts = [
        [int(TIMING * 6), int(-TIMING * 10)],
        [int(TIMING * 6), int(-TIMING * 16)],
        [int(TIMING * 6), int(-TIMING * 22)],
        [int(TIMING * 6), int(-TIMING * 28)],
    ]

    _code_order = [
        ['D', 4],
        ['F', 8],
    ]

    _parameters = [
        ['D', 0, 3],
        ['F', 4, 11],
    ]

    # [D:0..15,F:0..255]
    encode_parameters = [
        ['device', 0, 15],
        ['function', 0, 255],
    ]

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        normalized_code = []
        code = data[:]
        decoded = []

        tt = sum(abs(item) for item in code[:-1])

        mark, space = code[:2]
        code = code[2:]

        if not (
            self._match(mark, self._lead_in[0]) and
            self._match(space, self._lead_in[1])
        ):
            raise LeadInError

        normalized_code.extend(self._lead_in[:])

        mark, space = code[-2:]
        code = code[:-2]

        if not (
            self._match(self._lead_out[0], mark) and
            self._match(tt - self._lead_out[1], space)
        ):
            raise LeadOutError

        if len(code) > self.bit_count:
            raise TooManyBitsError
        if len(code) < self.bit_count:
            raise NotEnoughBitsError

        for i in range(0, len(code), 2):
            mark = code[i]
            space = code[i + 1]

            for j, (e_mark, e_space) in enumerate(self._bursts):
                if self._match(mark, e_mark) and self._match(space, e_space):
                    decoded.extend([j >> 1 & 1, j & 1])
                    normalized_code += [e_mark, e_space]
                    break
            else:
                raise IRStreamError

        params = dict(frequency=self.frequency)

        for key, start_bit, stop_bit in self._parameters:
            value = 0
            for i in range(start_bit, stop_bit + 1):
                value |= decoded[i] << (~i + stop_bit + 1)

            params[key] = protocol_base.IntegerWrapper(
                value,
                stop_bit + 1 - start_bit,
                self._bursts,
                self.encoding
            )

        normalized_code.append(self._lead_out[0])

        tt = sum(abs(item) for item in normalized_code)
        normalized_code.append(tt - self._lead_out[-1])

        code = protocol_base.IRCode(
            self,
            data[:],
            normalized_code,
            params
        )

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
        params = dict(
            D=device,
            F=function,
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
