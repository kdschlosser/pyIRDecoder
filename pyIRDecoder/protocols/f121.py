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
from . import DecodeError


TIMING = 422


class F121(protocol_base.IrProtocolBase):
    """
    IR decoder for the F121 protocol.
    """

    irp = (
        '{37.9k,422,lsb}<1,-3|3,-1>'
        '(D:3,H:1,F:8,-34,D:3,H:1,F:8,-88,D:3,H:1,F:8,-34,D:3,H:1,F:8)*'
        '{H=1}'
    )
    frequency = 37900
    bit_count = 48
    encoding = 'lsb'

    _lead_in = []
    _lead_out = []
    _middle_timings1 = [-TIMING * 34, -TIMING * 88, -TIMING * 34]
    _bursts = [[TIMING, -TIMING * 3], [TIMING * 3, -TIMING]]

    _code_order = [
        ['D', 3],
        ['F', 8],
    ]

    _parameters = [
        ['D', 0, 2],
        ['H', 3, 3],
        ['F', 4, 11],
        ['D1', 12, 14],
        ['H1', 15, 15],
        ['F1', 16, 23],
        ['D2', 24, 26],
        ['H2', 27, 27],
        ['F2', 28, 35],
        ['D3', 36, 38],
        ['H3', 39, 39],
        ['F3', 40, 47]
    ]
    # [D:0..7,F:0..255]
    encode_parameters = [
        ['device', 0, 7],
        ['function', 0, 255]
    ]

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        middle_bursts = {}

        for _, space in self._bursts:
            for mb in self._middle_timings1:
                middle_bursts[mb + space] = space

        new_code = []

        for i in range(0, len(data), 2):
            mark = data[i]
            space = data[i + 1]
            for e_space in middle_bursts.keys():
                if self._match(space, e_space):
                    new_code.extend([mark, middle_bursts[e_space]])
                    break
            else:
                new_code.extend([mark, space])

        if new_code == data:
            raise DecodeError

        code = protocol_base.IrProtocolBase.decode(self, new_code, frequency)

        if (
            code.device != code.d1 != code.d2 != code.d3 or
            code.h != code.h1 != 1 != code.h2 != code.h3 or
            code.function != code.f1 != code.f2 != code.f3
        ):
            raise DecodeError('Invalid checksum')

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
        h = 1

        packet1 = self._build_packet(
            D=device,
            H=h,
            F=function
        )

        packet2 = packet1[:]
        packet3 = packet1[:]
        packet4 = packet1[:]

        packet1[-1] += self._middle_timings1[0]
        packet2[-1] += self._middle_timings1[1]
        packet3[-1] += self._middle_timings1[2]

        params = dict(
            frequency=self.frequency,
            D=device,
            H=h,
            F=function,
            D1=device,
            H1=h,
            F1=function,
            D2=device,
            H2=h,
            F2=function,
            D3=device,
            H3=h,
            F3=function,
        )

        code = protocol_base.IRCode(
            self,
            (packet1[:] + packet2[:] + packet3[:] + packet4[:]) *
            (repeat_count + 1),
            ([packet1[:]] + [packet2[:]] + [packet3[:]] + [packet4[:]]) *
            (repeat_count + 1),
            params,
            repeat_count
        )
        return code
