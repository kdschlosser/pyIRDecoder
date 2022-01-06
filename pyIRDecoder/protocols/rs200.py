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

from typing import Sequence

# Local imports
from . import protocol_base
from . import (
    DecodeError,
    LeadOutError,
    TooManyBitsError,
    NotEnoughBitsError
)


TIMING = 1000 / 35.7


class Rs200(protocol_base.IrProtocolBase):
    """
    IR decoder for the Rs200 protocol.
    """

    irp = (
        '{35.7k,1,msb}<50p,-120p|21p,-120p>'
        '(25:6,(H4-1):2,(H3-1):2,(H2-1):2,(H1-1):2,P:1,'
        '(D-1):3,F:2,0:2,sum_:4,-1160p)*'
        '{P=~(#(D-1)+#F):1,sum_=9+((H4-1)*4+(H3-1))+'
        '((H2-1)*4+(H1-1))+(P*8+(D-1))+F*4}'
    )
    frequency = 35700
    bit_count = 26
    encoding = 'msb'

    _lead_in = []
    _lead_out = [-35854]
    _middle_timings = []
    _bursts = [[1401, -3361], [588, -3361]]

    _code_order = [
        ['H4', 2],
        ['H3', 2],
        ['H2', 2],
        ['H1', 2],
        ['D', 3],
        ['F', 2]
    ]

    _parameters = [
        ['C0', 0, 5],
        ['H4', 6, 7],
        ['H3', 8, 9],
        ['H2', 10, 11],
        ['H1', 12, 13],
        ['P', 14, 14],
        ['D', 15, 17],
        ['F', 18, 19],
        ['C1', 20, 21],
        ['CHECKSUM', 22, 25]
    ]
    # [H1:1..4,H2:1..4,H3:1..4,H4:1..4,D:1..6,F:0..2]
    encode_parameters = [
        ['device', 1, 6],
        ['function', 0, 2],
        ['h1', 1, 4],
        ['h2', 1, 4],
        ['h3', 1, 4],
        ['h4', 1, 4],
    ]

    @classmethod
    def _calc_checksum(
        cls,
        device: protocol_base.IntegerWrapper,
        function: protocol_base.IntegerWrapper,
        h1: protocol_base.IntegerWrapper,
        h2: protocol_base.IntegerWrapper,
        h3: protocol_base.IntegerWrapper,
        h4: protocol_base.IntegerWrapper
    ) -> Sequence[protocol_base.IntegerWrapper]:
        # {P=~(#(D-1)+#F):1,
        # sum_=9+((H4-1)*4+(H3-1))+((H2-1)*4+(H1-1))+(P*8+(D-1))+F*4}

        p = (device.num_one_bits + function.num_one_bits)[True:1:0]

        sum_ = (
            9 +
            (h4 * 4 + h3) +
            (h2 * 4 + h1) +
            (p * 8 + device) +
            function * 4
        )
        return p, sum_[:4:0]

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        original_code = data[:]
        code = data[:]
        normalized_code = []

        lead_out = code[-1]
        code = code[:-1]

        if not self._match(lead_out, self._lead_out[0]):
            raise LeadOutError

        code += [self._bursts[0][1]]

        decoded = []
        for i in range(0, len(code), 2):
            mark = code[i]
            space = code[i + 1]

            for j, (e_mark, e_space) in enumerate(self._bursts):
                if self._match(mark, e_mark) and self._match(space, e_space):
                    decoded += [j]
                    normalized_code += [e_mark, e_space]
                    break
            else:
                raise DecodeError('invalid burst pair')

        if len(decoded) > self.bit_count:
            raise TooManyBitsError
        elif len(decoded) < self.bit_count:
            raise NotEnoughBitsError

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

        normalized_code[-1] = self._lead_out[0]

        p, checksum = self._calc_checksum(
            params['D'],
            params['F'],
            params['H1'],
            params['H2'],
            params['H3'],
            params['H4']
        )

        if (
            checksum != params['CHECKSUM'] or
            p != params['P'] or
            params['C0'] != 25 or
            params['C1'] != 0
        ):
            raise DecodeError('Checksum failed')

        params['H4'] += 1
        params['H3'] += 1
        params['H2'] += 1
        params['H1'] += 1
        params['D'] += 1

        code = protocol_base.IRCode(
            self,
            original_code,
            normalized_code,
            params
        )

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
        h1: int,
        h2: int,
        h3: int,
        h4: int,
        repeat_count: int = 0
    ) -> protocol_base.IRCode:
        d = protocol_base.IntegerWrapper(
            device - 1,
            3,
            self._bursts,
            self.encoding
        )
        function = protocol_base.IntegerWrapper(
            function,
            2,
            self._bursts,
            self.encoding
        )
        h1_ = protocol_base.IntegerWrapper(
            h1 - 1,
            2,
            self._bursts,
            self.encoding
        )
        h2_ = protocol_base.IntegerWrapper(
            h2 - 1,
            2,
            self._bursts,
            self.encoding
        )
        h3_ = protocol_base.IntegerWrapper(
            h3 - 1,
            2,
            self._bursts,
            self.encoding
        )
        h4_ = protocol_base.IntegerWrapper(
            h4 - 1,
            2,
            self._bursts,
            self.encoding
        )
        
        p, checksum = self._calc_checksum(
            d,
            function,
            h1_,
            h2_,
            h3_,
            h4_
        )

        c0 = protocol_base.IntegerWrapper(
            25,
            6,
            self._bursts,
            self.encoding
        )

        c1 = protocol_base.IntegerWrapper(
            0,
            2,
            self._bursts,
            self.encoding
        )

        params = dict(
            C0=c0,
            C1=c1,
            D=d,
            P=p,
            F=function,
            H1=h1_,
            H2=h2_,
            H3=h3_,
            H4=h4_,
            CHECKSUM=checksum
        )

        packet = self._build_packet(**params)

        device = protocol_base.IntegerWrapper(
            device,
            4,
            self._bursts,
            self.encoding
        )
        h1 = protocol_base.IntegerWrapper(
            h1,
            3,
            self._bursts,
            self.encoding
        )
        h2 = protocol_base.IntegerWrapper(
            h2,
            3,
            self._bursts,
            self.encoding
        )
        h3 = protocol_base.IntegerWrapper(
            h3,
            3,
            self._bursts,
            self.encoding
        )
        h4 = protocol_base.IntegerWrapper(
            h4,
            3,
            self._bursts,
            self.encoding
        )

        params = dict(
            frequency=self.frequency,
            C0=c0,
            C1=c1,
            D=device,
            P=p,
            F=function,
            H1=h1,
            H2=h2,
            H3=h3,
            H4=h4,
            CHECKSUM=checksum
        )

        code = protocol_base.IRCode(
            self,
            packet[:] * (repeat_count + 1),
            [packet[:]] * (repeat_count + 1),
            params,
            repeat_count
        )

        return code
