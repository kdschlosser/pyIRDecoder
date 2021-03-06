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


TIMING = 600


class DirecTV(protocol_base.IrProtocolBase):
    """
    IR decoder for the DirecTV protocol.
    """
    irp = '{38k,600,msb}<1,-1|1,-2|2,-1|2,-2>(10,-2,(D:4,F:8,C:4,1,-30m,5,-2)*){C=7*(F:2:6)+5*(F:2:4)+3*(F:2:2)+(F:2)}'
    frequency = 38000
    bit_count = 16
    encoding = 'msb'

    _lead_in = [TIMING * 10, -TIMING * 2]
    _lead_out = [TIMING, -30000, TIMING * 5, -TIMING * 2]
    _bursts = [[TIMING, -TIMING], [TIMING, -TIMING * 2], [TIMING * 2, -TIMING], [TIMING * 2, -TIMING * 2]]

    _code_order = [
        ['D', 4],
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

    def _calc_checksum(self, function):
        # {C=7*(F:2:6)+5*(F:2:4)+3*(F:2:2)+(F:2)}
        c = (
            7 * self._get_bits(function, 6, 7) +
            5 * self._get_bits(function, 4, 5) +
            3 * self._get_bits(function, 2, 3) +
            self._get_bits(function, 0, 1)
        )

        return self._get_bits(c, 0, 3)

    def decode(self, data, frequency=0):
        if len(data) < 20:
            raise DecodeError('Invalid code')

        cleaned_code = []
        original_code = data[:]
        code = data[:]

        if (
            self._match(code[0], self._lead_in[0]) and
            self._match(code[1], self._lead_in[1])
        ):
            code = code[2:]

            cleaned_code += self._lead_in[:]

            if not len(code):
                self._last_code = [data[:], cleaned_code[:]]
                raise RepeatLeadIn

        elif isinstance(self._last_code, list):
            original_code = self._last_code[0][:] + original_code
            cleaned_code += self._last_code[1][:]
            self._last_code = None
        elif self._last_code is None:
            raise DecodeError('Invalid lead in')

        lead_out = code[-4:]
        code = code[:-4]

        for i, burst in enumerate(lead_out):
            e_burst = self._lead_out[i]

            if self._match(burst, e_burst):
                lead_out[i] = e_burst
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

        cleaned_code += lead_out

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

        checksum = self._calc_checksum(params['F'])

        if checksum != params['CHECKSUM']:
            raise DecodeError('Invalid checksum')

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
        checksum = self._calc_checksum(function)

        lead_in = self._lead_in[:]

        del self._lead_in[:]
        code = self._build_packet(
            list(self._get_timing(device, i) for i in range(0, 4, 2)),
            list(self._get_timing(function, i) for i in range(0, 8, 2)),
            list(self._get_timing(checksum, i) for i in range(0, 4, 2))
        )

        self._lead_in = lead_in[:]

        packet = [lead_in + code[:]]
        packet += [code[:]] * repeat_count

        params = dict(
            frequency=self.frequency,
            D=device,
            F=function,
        )

        code = protocol_base.IRCode(
            self,
            [lead_in[:] + code[:]],
            packet[:],
            params,
            repeat_count
        )

        return code

    def _test_decode(self):
        rlc = [
            [+6000, -1200],
            [
                +1200, -1200, +1200, -1200, +600, -1200, +1200, -1200, +1200, -1200, +600, -600, +1200, -1200,
                +1200, -1200, +600, -30000, +3000, -1200
            ]
        ]

        params = [
            None,
            dict(device=15, function=124)
        ]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(device=15, function=124)
        protocol_base.IrProtocolBase._test_encode(self, params)


DirecTV = DirecTV()
