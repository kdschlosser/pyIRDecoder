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
from . import DecodeError


TIMING = 1000.0 / 36.0


class Nokia12(protocol_base.IrProtocolBase):
    """
    IR decoder for the Nokia12 protocol.
    """
    irp = '{36k,1p,msb}<6,-10|6,-16|6,-22|6,-28>(15,-10,D:4,F:8,6,^100m)*'
    frequency = 36000
    bit_count = 12
    encoding = 'msb'

    _lead_in = [int(TIMING * 15), int(-TIMING * 10)]
    _lead_out = [int(TIMING), 108000]
    _middle_timings = []
    _bursts = [
        [int(TIMING * 6), int(-TIMING * 10)],
        [int(TIMING * 6), int(-TIMING * 16)],
        [int(TIMING * 6), int(-TIMING * 22)],
        [int(TIMING * 6), int(-TIMING * 28)]
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

    def decode(self, data, frequency=0):
        if not self._match(frequency, self.frequency, self.frequency_tolerance):
            raise DecodeError('Invalid frequency')

        cleaned_code = []
        original_code = data[:]
        code = data[:]

        mark, space = code[:2]
        code = code[2:]

        if (
                self._match(mark, self._lead_in[0]) and
                self._match(space, self._lead_in[1])
        ):
            cleaned_code += self._lead_in[:]

        mark, space = code[-2:]
        code = code[:-2]
        lead_out = []

        tt = sum(abs(item) for item in original_code[:-1])
        tt = -(self._lead_out[-1] - tt)
        if (
                self._match(self._lead_out[0], mark) and
                self._match(tt, space)
        ):
            lead_out += self._lead_out[:1]
        else:
            raise DecodeError('Invalid lead out')

        if len(code) > self.bit_count:
            raise DecodeError('To many bits')
        if len(code) < self.bit_count:
            raise DecodeError('Not enough bits')

        bits = []

        for i in range(0, len(code), 2):
            mark = code[i]
            space = code[i + 1]

            for j, (e_mark, e_space) in enumerate(self._bursts):
                if self._match(mark, e_mark) and self._match(space, e_space):
                    cleaned_code += [e_mark, e_space]
                    bits += [j]
                    break
            else:
                raise DecodeError('Invalid burst pair')

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

        cleaned_code += lead_out

        tt = sum(abs(item) for item in cleaned_code)
        tt = -(self._lead_out[1] - tt)
        cleaned_code += [tt]
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

        if self._last_code is not None:
            if self._last_code == code:
                return self._last_code

            self._last_code.repeat_timer.stop()

        self._last_code = code
        return code

    def encode(self, device, function, repeat_count=0):
        packet = self._build_packet(
            list(self._get_timing(device, i) for i in range(0, 4, 2)),
            list(self._get_timing(function, i) for i in range(0, 8, 2))
        )

        params = dict(
            frequency=self.frequency,
            D=device,
            F=function,
        )

        code = protocol_base.IRCode(
            self,
            [packet[:]],
            [packet[:]] * (repeat_count + 1),
            params,
            repeat_count
        )

        return code

    def _test_decode(self):
        rlc = [[
            417, -278, 167, -611, 167, -778, 167, -444, 167, -778, 167, -611, 167, -611,
            167, -94306,
        ]]

        params = [dict(device=11, function=122)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(device=11, function=122)
        protocol_base.IrProtocolBase._test_encode(self, params)


Nokia12 = Nokia12()
