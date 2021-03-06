# -*- coding: utf-8 -*-
#
# ***********************************************************************************
# MIT License
#
# Copyright (c) 2020 Kevin G. Schlosser
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is furnished
# to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
# CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
# OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# ***********************************************************************************

# Local imports
from . import protocol_base
from . import DecodeError, RepeatLeadIn


TIMING = 105


class Humax4Phase(protocol_base.IrProtocolBase):
    """
    IR decoder for the Humax4Phase protocol.
    """
    irp = '{56k,105,msb}<-2,2|-3,1|1,-3|2,-2>(T=0,(2,-2,D:6,S:6,T:2,F:7,~F:1,^95m,T=1)+)'
    frequency = 56000
    bit_count = 22
    encoding = 'msb'

    _lead_in = [TIMING * 2, -TIMING * 2]
    _lead_out = [95000]
    _middle_timings = []
    _bursts = [[-TIMING * 2, TIMING * 2], [-TIMING * 3, TIMING], [TIMING, -TIMING * 3], [TIMING * 2, -TIMING * 2]]

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

    def _calc_checksum(self, function):
        f = int(not self._get_bit(function, 0))
        return f

    def decode(self, data, frequency=0):
        cleaned_code = []
        original_code = data[:]
        code = data[:]

        mark, space = code[:2]
        code = code[2:]

        if self._match(mark, self._lead_in[0]):
            cleaned_code += [self._lead_in[0]]
        else:
            raise DecodeError('Invalid lead in')

        if self._match(space, self._lead_in[1]):
            cleaned_code += [self._lead_in[1]]

        else:
            for mark, _ in self._bursts:
                if self._match(space, self._lead_in[1] + mark):
                    cleaned_code += [self._lead_in[1]]
                    code.insert(0, mark)
                    break

            else:
                raise DecodeError('Invalid lead in')

        bits = []

        while code:
            try:
                mark, space = code[:2]
                code = code[2:]
            except ValueError:
                try:
                    space = code.pop(0)
                except IndexError:
                    raise DecodeError('Invalid number of pairs')

                tt = sum(abs(item) for item in original_code[:-1])

                if self._match(space, -(self._lead_out[0] - tt)):
                    tt = sum(abs(item) for item in cleaned_code)
                    cleaned_code += [-(self._lead_out[0] - tt)]
                    continue

            for i, (e_mark, e_space) in enumerate(self._bursts):
                if not self._match(mark, e_mark):
                    continue

                if mark < 0 < e_mark or mark > 0 > e_mark:
                    continue

                if self._match(space, e_space):
                    cleaned_code += [e_mark, e_space]
                    bits += [i]
                    break

                if len(code) == 0:
                    tt = sum(abs(item) for item in original_code[:-1])

                    if self._match(space, -(self._lead_out[0] - tt) + e_space):
                        cleaned_code += [e_mark, e_space]
                        bits += [i]
                        tt = sum(abs(item) for item in cleaned_code)
                        cleaned_code += [-(self._lead_out[0] - tt)]
                        break

                    raise DecodeError('Invalid lead out')

                for e_mark_2, _ in self._bursts:
                    if e_mark_2 == e_mark:
                        continue

                    if space < 0 < e_mark_2 or space > 0 > e_mark_2:
                        continue

                    if self._match(space, e_space + e_mark_2):
                        cleaned_code += [e_mark, e_space]
                        bits += [i]
                        code.insert(0, e_mark_2)
                        break
                else:
                    raise DecodeError('Invalid burst')

                break

            else:
                raise DecodeError('Invalid burst')

        if code:
            raise DecodeError('To many burst pairs')

        if len(bits) * 2 > self.bit_count:
            raise DecodeError('To many bits')
        if len(bits) * 2 < self.bit_count:
            raise DecodeError('Not enough bits')

        decoded = []

        for num in bits:
            decoded += [self._get_bit(num, 1), self._get_bit(num, 0)]

        params = dict(frequency=self.frequency)

        for key, start_bit, stop_bit in self._parameters:
            bits = []
            value = 0
            for i in range(start_bit, stop_bit + 1):
                bits.insert(0, decoded[i])

            for i, bit in enumerate(bits):
                value = self._set_bit(value, i, bit)

            params[key] = value

        normalized_code = []

        for pulse in cleaned_code:
            if (
                len(normalized_code) and
                (normalized_code[-1] < 0 > pulse or normalized_code[-1] > 0 < pulse)
            ):
                normalized_code[-1] += pulse
                continue

            normalized_code += [pulse]

        code = protocol_base.IRCode(self, original_code, normalized_code, params)

        f_checksum = self._calc_checksum(code.function)

        if f_checksum != code.f_checksum:
            raise DecodeError('Invalid checksum')

        if code.toggle == 0:
            if self._last_code is not None:
                self._last_code.repeat_timer.stop()
            self._last_code = code
            raise RepeatLeadIn

        if code.toggle == 1:
            if self._last_code is None:
                raise DecodeError('invalid frame')
            if self._last_code != code:
                raise DecodeError('Invalid frame')

            return self._last_code

        raise DecodeError('Invalid repeat')

    def _get_timing(self, num, index):
        value = self._get_bits(num, index, index + 1)
        return self._bursts[value]

    def encode(self, device, sub_device, function, repeat_count=0):
        func_checksum = self._calc_checksum(function)
        func = 0
        for i in range(7):
            func = self._set_bit(func, i + 1, self._get_bit(function, i))

        func = self._set_bit(func, 0, self._get_bit(func_checksum, 0))

        toggle = 0

        packet = self._build_packet(
            list(self._get_timing(device, i) for i in range(0, 6, 2)),
            list(self._get_timing(sub_device, i) for i in range(0, 6, 2)),
            list(self._get_timing(toggle, i) for i in range(0, 2, 2)),
            list(self._get_timing(func, i) for i in range(0, 8, 2)),
        )

        toggle = 1

        packet2 = self._build_packet(
            list(self._get_timing(device, i) for i in range(0, 6, 2)),
            list(self._get_timing(sub_device, i) for i in range(0, 6, 2)),
            list(self._get_timing(toggle, i) for i in range(0, 2, 2)),
            list(self._get_timing(func, i) for i in range(0, 8, 2)),
        )

        params = dict(
            frequency=self.frequency,
            D=device,
            S=sub_device,
            F=function,
        )

        code = protocol_base.IRCode(
            self,
            [packet[:], packet2[:]],
            [packet[:]] + ([packet2[:]] * (repeat_count + 1)),
            params,
            repeat_count
        )

        return code

    def _test_decode(self):
        rlc = [
            [
                +210, -210, +210, -420, +210, -315, +105, -315, +315, -420, +210, -210, +315, -315, +105, -630, +210,
                -90275
            ],
            [
                +210, -210, +210, -420, +210, -315, +105, -315, +315, -420, +210, -315, +210, -315, +105, -630, +210,
                -90275
            ]

        ]

        params = [
            dict(device=49, function=83, sub_device=28, toggle=0),
            dict(device=49, function=83, sub_device=28, toggle=1)
        ]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(device=49, function=83, sub_device=28)
        protocol_base.IrProtocolBase._test_encode(self, params)


Humax4Phase = Humax4Phase()


