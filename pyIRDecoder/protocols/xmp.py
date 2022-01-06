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
    NotEnoughBitsError,
    TooManyBitsError,
    IRException,
    RepeatLeadInError,
    RepeatLeadOutError
)

TIMING = 290


class XMP(protocol_base.IrProtocolBase):
    """
    IR decoder for the Grundig16 protocol.
    """
    irp = (
        '{38k,136,msb}'
        '<210u,-760u|210u,-896u|210u,-1032u|210u,-1168u|210u,-1304u|'
        '210u,-1449u|210u,-1576u|210u,-1712u|210u,-1848u|210u,-1984u|'
        '210u,-2120u|210u,-2256u|210u,-2392u|210u,-2528u|210u,-2664u|'
        '210u,-2800u>'
        '([T=0][T=8],S:4:4,C1:4,S:4,15:4,OEM:8,D:8,210u,'
        '-13.8m,S:4:4,C2:4,T:4,S:4,F:16,210u,-80.4m)+'
        '{C1=-(S+S::4+15+OEM+OEM::4+D+D::4),C2=-(S+S::4+T+F+F::4+F::8+F::12)}'
    )
    frequency = 38000

    bit_count = 0
    _bit_count1 = 64
    _bit_count2 = 32

    encoding = 'msb'
    _lead_out1 = [210, -80400]
    _lead_out2 = [210, -13800]

    _bursts = [
        [210, -760],
        [210, -896],
        [210, -1032],
        [210, -1168],
        [210, -1304],
        [210, -1449],
        [210, -1576],
        [210, -1712],
        [210, -1848],
        [210, -1984],
        [210, -2120],
        [210, -2256],
        [210, -2392],
        [210, -2528],
        [210, -2664],
        [210, -2800]
    ]
    _code_order = [
        ['D', 8],
        ['S', 8],
        ['F', 16],
        ['OEM', 8]
    ]

    _parameters1 = [
        ['S1', 0, 3],
        ['C1', 4, 7],
        ['S2', 8, 11],
        ['C3', 12, 15],
        ['OEM', 16, 23],
        ['D', 24, 31],
        ['S3', 32, 35],
        ['C2', 36, 39],
        ['T', 40, 43],
        ['S4', 44, 47],
        ['F', 48, 63]
    ]

    _parameters2 = [
        ['S1', 0, 3],
        ['C1', 4, 7],
        ['S2', 8, 11],
        ['C3', 12, 15],
        ['OEM', 16, 23],
        ['D', 24, 31]
    ]
    _parameters3 = [
        ['S3', 0, 3],
        ['C2', 4, 7],
        ['T', 8, 11],
        ['S4', 12, 15],
        ['F', 16, 31]
    ]

    # [F:0..65535,D:0..255,S:0..255,OEM:0..255=68]
    _encode_params = [
        ['function', 0, 65535],
        ['device', 0, 255],
        ['sub_device', 0, 255],
        ['oem', 0, 255]
    ]

    _prefix_code = None

    @staticmethod
    def _calc_checksum(
        function: protocol_base.IntegerWrapper,
        device: protocol_base.IntegerWrapper,
        sub_device: protocol_base.IntegerWrapper,
        oem: protocol_base.IntegerWrapper,
        toggle: protocol_base.IntegerWrapper
    ) -> Sequence[protocol_base.IntegerWrapper]:
        # {C1=-(S+S::4+15+OEM+OEM::4+D+D::4),C2=-(S+S::4+T+F+F::4+F::8+F::12)}
        c1 = -(
            sub_device +
            sub_device[:4:4] +
            15 +
            oem +
            oem[:4:4] +
            device +
            device[:4:4]
        )
        c2 = -(
            sub_device +
            sub_device[:4:4] +
            toggle +
            function +
            function[:12:4] +
            function[:8:8] +
            function[:4:12]
        )
        return c1[:4:0], c2[:4:0]

    def _process_code(
        self,
        code: list,
        lead_out: list
    ) -> protocol_base.IRCode:
        decoded = []
        original_code = code[:]

        e_mark, e_space = lead_out
        mark, space = code[-2:]
        code = code[:-2]

        if (
            not self._match(mark, e_mark) or
            not self._match(space, e_space)
        ):
            raise LeadOutError

        normalized_code = []

        for i in range(0, len(code), 2):
            mark = code[i]
            space = code[i + 1]
            for j, (e_mark, e_space) in enumerate(self._bursts):
                if (
                    self._match(mark, e_mark) and
                    self._match(space, e_space)
                ):
                    normalized_code.extend([e_mark, e_space])
                    for k in range(3, -1, -1):
                        decoded.append((j >> k) & 1)
                    break
            else:
                e_mark, e_space = self._middle_timings
                if (
                    not self._match(mark, e_mark) or
                    not self._match(space, e_space)
                ):
                    raise DecodeError('Invalid burst pair')

                normalized_code.extend([e_mark, e_space])

        if len(decoded) < self.bit_count:
            raise NotEnoughBitsError
        elif len(decoded) > self.bit_count:
            print(len(decoded), ':', self.bit_count)
            raise TooManyBitsError(str(original_code))

        params = dict(frequency=self.frequency)

        for param, start, stop in self._parameters:
            value = 0

            for i in range(start, stop + 1):
                value |= decoded[i] << (~i + stop + 1)

            params[param] = protocol_base.IntegerWrapper(
                value,
                stop + 1 - start,
                self._bursts,
                self.encoding
            )

        normalized_code.extend(lead_out[:])

        code = protocol_base.IRCode(
            self,
            original_code,
            normalized_code,
            params
        )
        return code

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        tolerance = self.tolerance
        self.tolerance = 2

        self.bit_count = self._bit_count1
        self._parameters = self._parameters1[:]
        self._lead_out = self._lead_out1
        self._middle_timings = self._lead_out2

        try:
            code = self._process_code(data[:], self._lead_out[:])
            self.tolerance = tolerance
        except LeadOutError:
            self.bit_count = self._bit_count2
            self._parameters = self._parameters2[:]
            self._lead_out = self._lead_out2
            self._middle_timings = []
            try:
                code = self._process_code(data[:], self._lead_out[:])
            except IRException:
                self.tolerance = tolerance
                raise

            self._prefix_code = code
            self.tolerance = tolerance
            raise RepeatLeadInError

        except NotEnoughBitsError:
            if self._prefix_code is None:
                raise DecodeError('Invalid code')

            self.bit_count = self._bit_count2
            self._parameters = self._parameters3[:]
            self._middle_timings = []
            try:
                code = self._process_code(data[:], self._lead_out[:])
            except IRException:
                self.tolerance = tolerance
                raise

            self.tolerance = tolerance
            self._prefix_code += code
            code = self._prefix_code
            self._prefix_code = None

        if code.c3 != 15:
            raise DecodeError('Invalid checksum')

        if code.s1 != code.s3:
            raise DecodeError('Invalid checksum')

        if code.s2 != code.s4:
            raise DecodeError('Invalid checksum')

        # noinspection PyProtectedMember
        code._data['S'] = code.s1 << 4 | code.s2

        c1, c2 = self._calc_checksum(
            code.function,
            code.device,
            code.sub_device,
            code.oem,
            code.toggle
        )

        if c1 != code.c1:
            raise DecodeError('invalid checksum')

        if c2 != code.c2:
            raise DecodeError('Invalid checksum')

        if self._last_code is not None:
            if code.toggle == 0 and self._last_code == code:
                return self._last_code

            self._last_code.repeat_timer.stop()
            self._last_code = None

            if code.toggle == 8:
                raise RepeatLeadOutError

        self._last_code = code
        return code

    def encode(
        self,
        device: int,
        sub_device: int,
        function: int,
        oem: int,
        repeat_count: int = 0
    ) -> protocol_base.IRCode:

        function = protocol_base.IntegerWrapper(
            function,
            16,
            self._bursts,
            self.encoding
        )
        device = protocol_base.IntegerWrapper(
            device,
            8,
            self._bursts,
            self.encoding
        )
        sub_device = protocol_base.IntegerWrapper(
            sub_device,
            8,
            self._bursts,
            self.encoding
        )
        oem = protocol_base.IntegerWrapper(
            oem,
            8,
            self._bursts,
            self.encoding
        )
        toggle = protocol_base.IntegerWrapper(
            0,
            4,
            self._bursts,
            self.encoding
        )
        c3 = protocol_base.IntegerWrapper(
            15,
            4,
            self._bursts,
            self.encoding
        )

        s1 = s3 = sub_device[:4:4]
        s2 = s4 = sub_device[:4:0]
        c1, c2 = self._calc_checksum(function, device, sub_device, oem, toggle)

        self.__class__._lead_out = self.__class__._lead_out1

        packet1 = self._build_packet(
            s1.timings,
            c1.timings,
            s2.timings,
            c3.timings,
            oem.timings,
            device.timings,
            self.__class__._lead_out2[:],
            s3.timings,
            c2.timings,
            toggle.timings,
            s4.timings,
            function.timings
        )

        toggle = protocol_base.IntegerWrapper(
            8,
            4,
            self._bursts,
            self.encoding
        )
        c1, c2 = self._calc_checksum(function, device, sub_device, oem, toggle)

        packet2 = self._build_packet(
            s1.timings,
            c1.timings,
            s2.timings,
            c3.timings,
            oem.timings,
            device.timings,
            self.__class__._lead_out2[:],
            s3.timings,
            c2.timings,
            toggle.timings,
            s4.timings,
            function.timings
        )

        params = dict(
            frequency=self.frequency,
            D=device,
            S=sub_device,
            F=function,
            OEM=oem
        )

        code = protocol_base.IRCode(
            self,
            (packet1[:] * (repeat_count + 1)) + packet2[:],
            [packet1[:]] * (repeat_count + 1) + [packet2[:]],
            params,
            repeat_count
        )
        return code
