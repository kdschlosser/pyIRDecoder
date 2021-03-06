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
from . import DecodeError, RepeatLeadOut


TIMING = 1000.0 / 36.0


class Nokia32(protocol_base.IrProtocolBase):
    """
    IR decoder for the Nokia32 protocol.
    """
    irp = '{36k,1p,msb}<6,-10|6,-16|6,-22|6,-28>((15,-10,D:8,S:8,T:1,X:7,F:8,6,^100m)*,T=1-T)'
    frequency = 36000
    bit_count = 32
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
        ['D', 8],
        ['S', 8],
        ['E', 7],
        ['F', 8]
    ]

    _parameters = [
        ['D', 0, 7],
        ['S', 8, 15],
        ['T', 16, 16],
        ['E', 17, 23],
        ['F', 24, 31],
    ]
    # [D:0..255,F:0..255]
    encode_parameters = [
        ['device', 0, 255],
        ['sub_device', 0, 255],
        ['function', 0, 255],
        ['extended_function', 0, 127],
    ]

    _has_repeat_lead_out = True

    def decode(self, data, frequency=0):
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
            if (
                self._last_code == code and
                self._last_code.toggle == code.toggle
            ):
                return self._last_code

            last_code = self._last_code
            self._last_code.repeat_timer.stop()

            if last_code == code:
                raise RepeatLeadOut

        self._last_code = code
        return code

    def encode(self, device, sub_device, function, extended_function, repeat_count=0):
        toggle = 0

        x = self._set_bit(extended_function, 7, self._get_bit(toggle, 0))

        code = self._build_packet(
            list(self._get_timing(device, i) for i in range(0, 8, 2)),
            list(self._get_timing(sub_device, i) for i in range(0, 8, 2)),
            list(self._get_timing(x, i) for i in range(0, 8, 2)),
            list(self._get_timing(function, i) for i in range(0, 8, 2))
        )

        toggle = 1
        x = self._set_bit(extended_function, 7, self._get_bit(toggle, 0))

        lead_out = self._build_packet(
            list(self._get_timing(device, i) for i in range(0, 8, 2)),
            list(self._get_timing(sub_device, i) for i in range(0, 8, 2)),
            list(self._get_timing(x, i) for i in range(0, 8, 2)),
            list(self._get_timing(function, i) for i in range(0, 8, 2))
        )

        packet = [code] * (repeat_count + 1)
        packet += [lead_out]

        params = dict(
            frequency=self.frequency,
            D=device,
            S=sub_device,
            F=function,
            E=extended_function
        )

        code = protocol_base.IRCode(
            self,
            [code[:], lead_out[:]],
            packet[:],
            params,
            repeat_count
        )

        return code

    def _test_decode(self):
        rlc = [[
            417, -278, 167, -444, 167, -278, 167, -611, 167, -778, 167, -444, 167, -778, 167, -444,
            167, -278, 167, -278, 167, -278, 167, -611, 167, -278, 167, -278, 167, -278, 167, -611,
            167, -444, 167, -89361,
        ]]

        params = [dict(function=9, toggle=0, device=75, x=8, sub_device=116)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(function=9, toggle=0, device=75, x=8, sub_device=116)
        protocol_base.IrProtocolBase._test_encode(self, params)


Nokia32 = Nokia32()
