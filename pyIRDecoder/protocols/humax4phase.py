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


TIMING = 105


class Humax4Phase(protocol_base.IrProtocolBase):
    """
    IR decoder for the Humax4Phase protocol.
    """
    irp = (
        '{56k,105,msb}<-2,2|-3, 1|1,-3|2,-2>'
        '(T=0,(2,-2,D:6,S:6,T:2,F:7,~F:1,^95m,T=1)+)'
    )

    frequency = 56000
    bit_count = 22
    encoding = 'msb'

    _lead_in = [TIMING * 2, -TIMING * 2]
    _lead_out = [95000]
    _middle_timings = []
    _bursts = [
        [-TIMING * 2, TIMING * 2],
        [-TIMING * 3, TIMING],
        [TIMING, -TIMING * 3],
        [TIMING * 2, -TIMING * 2]
    ]

    _code_order = [
        ['D', 6],
        ['S', 6],
        ['F', 7]
    ]

    _parameters = [
        ['D', 0, 5],
        ['S', 6, 11],
        ['T', 12, 13],
        ['F', 14, 20],
        ['F_CHECKSUM', 21, 21]
    ]
    # [D:0..63,S:0..63,F:0..127]
    encode_parameters = [
        ['device', 0, 63],
        ['sub_device', 0, 63],
        ['function', 0, 127]
    ]

    @staticmethod
    def _calc_checksum(
        function: protocol_base.IntegerWrapper
    ) -> protocol_base.IntegerWrapper:
        return function[True:1:0]

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        cleaned_code = []
        original_code = data[:]
        code = data[:]

        mark, space = code[:2]
        code = code[2:]

        if self._match(mark, self._lead_in[0]):
            cleaned_code += [self._lead_in[0]]
        else:
            raise LeadInError

        if self._match(space, self._lead_in[1]):
            cleaned_code += [self._lead_in[1]]

        else:
            for mark, _ in self._bursts:
                if self._match(space, self._lead_in[1] + mark):
                    cleaned_code += [self._lead_in[1]]
                    code.insert(0, mark)
                    break
            else:
                raise LeadInError

        pairs = []

        tt = sum(abs(item) for item in original_code[:-1])
        lead_out = code[-1]
        code = code[:-1]

        if self._match(lead_out, tt - self._lead_out[0]):
            pass

        else:
            for _, burst in self._bursts:
                if self._match(
                    lead_out,
                    (tt + abs(burst)) - self._lead_out[0]
                ):
                    code.append(burst)
                    break
            else:
                raise LeadOutError

        while code:
            try:
                timings = code[:2]
                code = code[2:]
            except ValueError:
                break

            for bursts in self._bursts:
                if (
                    self._match(timings[0], bursts[0]) and
                    self._match(timings[1], bursts[1])
                ):
                    pairs.append(bursts)
                    break

                if self._match(timings[0], bursts[0]):
                    for timing, _ in self._bursts:
                        if (
                            timing < 0 > bursts[-1] or
                            timing > 0 < bursts[-1]
                        ):

                            if self._match(timings[-1], timing + bursts[-1]):
                                pairs.append(bursts)
                                code.insert(0, timing)
                                break

                    else:
                        continue

                    break

            else:
                raise DecodeError(str(timings))

        if code:
            raise IRStreamError

        decoded = []

        for pair in pairs:
            num = self._bursts.index(pair)
            decoded.extend([num >> 1 & 1, num & 1])
            cleaned_code.extend(pair)

        if len(decoded) > self.bit_count:
            raise TooManyBitsError
        if len(decoded) < self.bit_count:
            raise NotEnoughBitsError

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

        normalized_code = []

        tt = sum(abs(item) for item in cleaned_code)
        cleaned_code.append(tt - self._lead_out[0])

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

        f_checksum = self._calc_checksum(code.function)

        if f_checksum != code.f_checksum:
            raise DecodeError('Invalid checksum')

        if code.toggle == 0:
            if self._last_code is not None:
                self._last_code.repeat_timer.stop()
            self._last_code = code
            raise RepeatLeadInError

        if code.toggle == 1:
            last_code = self._last_code
            self._last_code = None

            if last_code is None:
                raise DecodeError('invalid frame')
            if last_code != code:
                raise DecodeError('Invalid frame')

            self._last_code = code

            return code

        raise DecodeError('Invalid repeat')

    def encode(
        self,
        device: int,
        sub_device: int,
        function: int,
        repeat_count: int = 0
    ) -> protocol_base.IRCode:
        function = protocol_base.IntegerWrapper(
            function,
            7,
            self._bursts,
            self.encoding

        )

        func_checksum = self._calc_checksum(function)

        code = protocol_base.IntegerWrapper(
            device << 16 |
            sub_device << 10 |
            0 << 8 |
            function << 1 |
            func_checksum,
            22,
            self._bursts,
            self.encoding
        )

        packet = self._build_packet(code.timings)
        code = protocol_base.IntegerWrapper(
            device << 16 |
            sub_device << 10 |
            1 << 8 |
            function << 1 |
            func_checksum,
            22,
            self._bursts,
            self.encoding
        )

        packet2 = self._build_packet(code.timings)

        params = dict(
            frequency=self.frequency,
            D=device,
            S=sub_device,
            F=function,
            T=1,
            F_CHECKSUM=func_checksum
        )

        code = protocol_base.IRCode(
            self,
            packet[:] + (packet2[:] * (repeat_count + 1)),
            [packet[:]] + ([packet2[:]] * (repeat_count + 1)),
            params,
            repeat_count
        )

        return code
