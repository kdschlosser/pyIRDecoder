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
    LeadOutError,
    TooManyBitsError,
    NotEnoughBitsError
)


TIMING = 3000


# TODO: finish
class PID0083(protocol_base.IrProtocolBase):
    """
    IR decoder for the pid0083 protocol.
    """
    irp = '{42.3k,3000,lsb}<1,-3,1,-7|1,-7,1,-3>(F:5,1,-27)*'
    frequency = 42300
    bit_count = 5
    encoding = 'lsb'

    _lead_in = []
    _lead_out = [TIMING, -TIMING * 27]
    _middle_timings = []
    _bursts = [
        [TIMING, -TIMING * 3, TIMING, -TIMING * 7],
        [TIMING, -TIMING * 7, TIMING, -TIMING * 3]
    ]

    _code_order = [
        ['F', 5],
    ]

    _parameters = [
        ['F', 0, 4]
    ]
    # [F:0..31]
    encode_parameters = [
        ['function', 0, 31],
    ]

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        mark, space = data[-2:]

        if (
            not self._match(mark, self._lead_out[0]) or
            not self._match(space, self._lead_out[1])
        ):
            raise LeadOutError

        if len(data[:-2]) // 4 > self.bit_count:
            raise TooManyBitsError

        elif len(data[:-2]) // 4 < self.bit_count:
            raise NotEnoughBitsError

        if len(data[:-2]) % 4:
            raise DecodeError('Invalid burst pairs')

        decoded = []
        cleaned = []
        for i in range(0, len(data[:-2]), 4):
            burst_mark1 = data[i]
            burst_space1 = data[i + 1]
            burst_mark2 = data[i + 2]
            burst_space2 = data[i + 3]

            for j, (mark1, space1, mark2, space2) in enumerate(self._bursts):
                if (
                    self._match(burst_mark1, mark1) and
                    self._match(burst_space1, space1) and
                    self._match(burst_mark2, mark2) and
                    self._match(burst_space2, space2)
                ):
                    decoded += [j]

                    cleaned += [mark1, space1, mark2, space2]
                    break
            else:
                raise DecodeError('Invalid burst sequence')

        cleaned += self._lead_out[:]

        function = 0

        for i in range(len(decoded)):
            function |= decoded[i] << i

        params = dict(
            F=function,
            frequency=self.frequency
        )

        code = protocol_base.IRCode(self, data[:], cleaned, params)

        if self._last_code is not None:
            if self._last_code == code:
                return self._last_code

            self._last_code.repeat_timer.stop()
            self._last_code = None
        self._last_code = code

        return code

    def encode(
        self,
        function: int,
        repeat_count: int = 0
    ) -> protocol_base.IRCode:
        params = dict(
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
