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
    RepeatLeadOutError,
    TooManyBitsError,
    NotEnoughBitsError
)


TIMING = 578


class Grundig16(protocol_base.IrProtocolBase):
    """
    IR decoder for the Grundig16 protocol.
    """
    irp = (
        '{35.7k,578,msb}<-4,2|-3,1,-1,1|-2,1,-2,1|-1,1,-3,1>'
        '(806u,-2960u,1346u,T:1,F:8,D:7,-100)*'
    )
    frequency = 35700
    bit_count = 16
    encoding = 'msb'

    _lead_in = [806, -2960, 1346]
    _lead_out = [-TIMING * 100]
    _middle_timings = []
    _bursts = [
        [-TIMING * 4, TIMING * 2],
        [-TIMING * 3, TIMING, -TIMING, TIMING],
        [-TIMING * 2, TIMING, -TIMING * 2, TIMING],
        [-TIMING, TIMING, -TIMING * 3, TIMING],
    ]

    _repeat_lead_in = [TIMING * 16, -TIMING * 8]
    _repeat_lead_out = [TIMING, 108000]
    _repeat_bursts = []

    _code_order = [
        ['D', 7],
        ['F', 8],
    ]
    _parameters = [
        ['T', 0, 0],
        ['F', 1, 8],
        ['D', 9, 15],
    ]
    # [D:0..127,F:0..255,T@:0..1=0]
    encode_parameters = [
        ['device', 0, 127],
        ['function', 0, 255],
    ]

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        normalized_code = []
        code = data[:]
        original_code = data[:]
        for i, timing in enumerate(self._lead_in):
            if not self._match(code[i], timing):
                raise DecodeError('Invalid lead in')

            normalized_code.append(timing)

        code = code[3:]

        lead_out = code[-1]
        code = code[:-1]

        if not self._match(lead_out, self._lead_out[0]):
            raise DecodeError('Invalid lead out')

        decoded = []

        while code:
            for i, bursts in enumerate(self._bursts):
                try:
                    timings = code[:len(bursts)]
                except ValueError:
                    raise DecodeError

                for j, burst in enumerate(bursts):
                    timing = timings[j]
                    if not self._match(timing, burst):
                        break
                else:
                    normalized_code.extend(bursts)
                    code = code[len(bursts):]
                    decoded.extend([i >> 1 & 1, i & 1])
                    break
            else:
                raise DecodeError('Invalid bursts')

        if len(decoded) > self.bit_count:
            raise TooManyBitsError(str(decoded))
        elif len(decoded) < self.bit_count:
            raise NotEnoughBitsError(str(decoded))

        params = dict(frequency=self.frequency)

        for param, start_bit, stop_bit in self._parameters:
            value = 0

            for i in range(start_bit, stop_bit + 1):
                value |= decoded[i] << (~i + stop_bit + 1)

            params[param] = protocol_base.IntegerWrapper(
                value,
                stop_bit + 1 - start_bit,
                self._bursts,
                self.encoding
            )

        normalized_code.append(self._lead_out[0])

        code = protocol_base.IRCode(
            self,
            original_code,
            normalized_code,
            params
        )

        if code.toggle == 1:
            raise RepeatLeadOutError

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

        value = 0 << 15 | function << 7 | device
        value = protocol_base.IntegerWrapper(
            value,
            16,
            self._bursts,
            self.encoding
        )

        packet = self._build_packet(value.timings)

        value = 1 << 15 | function << 7 | device

        value = protocol_base.IntegerWrapper(
            value,
            16,
            self._bursts,
            self.encoding
        )

        repeat_lead_out = self._build_packet(value.timings)

        params = dict(
            frequncy=self.frequency,
            D=device,
            F=function,
            T=0
        )

        code = protocol_base.IRCode(
            self,
            (packet[:] * (repeat_count + 1)) + repeat_lead_out[:],
            ([packet[:]] * (repeat_count + 1)) + [repeat_lead_out[:]],
            params,
            repeat_count
        )
        return code
