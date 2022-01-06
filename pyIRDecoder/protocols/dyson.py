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
from . import IRException, RepeatLeadInError, DecodeError


TIMING = 780


class Dyson(protocol_base.IrProtocolBase):
    """
    IR decoder for the Dyson protocol.
    """
    irp = (
        '{38k,780,lsb}<1,-1|1,-2>'
        '(3,-1,D:7,F:6,T:-2,1,-100m,'
        ' 3,-1,D:7,F:6,T:-2,1,-60m,'
        '(3,-1,1:1,1,-60m)*)'
    )
    frequency = 38000
    bit_count = 0
    _bit_count1 = 15
    _bit_count2 = 30
    encoding = 'lsb'

    _lead_in = [TIMING * 3, -TIMING]
    _lead_out = [TIMING, -60000]
    _middle_timings = [(TIMING, -100000), (TIMING * 3, -TIMING)]
    _bursts = [[TIMING, -TIMING], [TIMING, -TIMING * 2]]

    _backup_middle_timings = _middle_timings[:]
    _backup_lead_out = _lead_out[:]

    _repeat_lead_in = [TIMING * 3, -TIMING]
    _repeat_lead_out = [TIMING, -60000]
    _repeat_bursts = [[TIMING, -TIMING], [TIMING, -TIMING * 3]]

    repeat_timeout = (TIMING * 9) + 70000

    _code_order = [
        ['D', 7],
        ['F', 6]
    ]

    _parameters = [
        ['D', 0, 6],
        ['F', 7, 12],
        ['T', 13, 14],
        ['D1', 15, 21],
        ['F1', 22, 27],
        ['T1', 28, 29]
    ]
    # [D:0..127,F:0..63,T:0..3=0]
    encode_parameters = [
        ['device', 0, 127],
        ['function', 0, 63],
        ['toggle', 0, 3]
    ]

    _sequence = []

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        self._middle_timings = self._backup_middle_timings[:]
        self._lead_out = self._backup_lead_out[:]
        self.bit_count = self._bit_count2

        try:
            code = protocol_base.IrProtocolBase.decode(self, data, frequency)

            if code.device != code.d1 or code.function != code.f1:
                raise DecodeError('Checksum failed')

            original_rlc = code.original_rlc
            normalized_rlc = code.normalized_rlc
            params = dict(
                D=code.device,
                F=code.function,
                T=code.toggle[:-2:],
                D1=code.device,
                F1=code.function,
                T1=code.toggle[:-2:],
                frequency=self.frequency
            )

            code = protocol_base.IRCode(
                self,
                original_rlc,
                normalized_rlc,
                params
            )

            if self._last_code is not None:
                if self._last_code == code:
                    return self._last_code

                self._last_code.repeat_timer.stop()
                self._last_code = None

            self._last_code = code
            return code

        except IRException:

            if self._last_code is not None:
                repeat_packet = (
                    self._repeat_lead_in[:] +
                    self._bursts[1][:] +
                    self._repeat_lead_out[:]
                )

                if len(repeat_packet) == len(data):
                    for i, item in enumerate(data):
                        if not self._match(item, repeat_packet[i]):
                            break
                    else:
                        return self._last_code

        if len(self._sequence) == 0:
            self._lead_out = list(self._backup_middle_timings[0])
            del self._middle_timings[:]

        elif len(self._sequence) == 1:
            self._lead_out = self._backup_lead_out[:]
            del self._middle_timings[:]

        self.bit_count = self._bit_count1
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)

        if len(self._sequence) == 0:
            self._sequence.append(code)
            raise RepeatLeadInError

        original_rlc = (
                self._sequence[0].original_rlc + code.original_rlc
        )
        normalized_rlc = (
                self._sequence[0].normalized_rlc + code.normalized_rlc
        )
        params = dict(
            D=self._sequence[0].device,
            F=self._sequence[0].function,
            T=self._sequence[0].toggle,
            D1=code.device,
            F1=code.function,
            T1=code.toggle[:-2:],
            frequency=self.frequency
        )

        code = protocol_base.IRCode(
            self,
            original_rlc,
            normalized_rlc,
            params
        )

        if code.device != code.d1 or code.function != code.f1:
            raise DecodeError('Checksum failed')

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
        toggle: int,
        repeat_count=0
    ):
        toggle = protocol_base.IntegerWrapper(
            toggle,
            2,
            self._bursts,
            self.encoding
        )[:-2:]

        lead_out = self._lead_out

        self._lead_out = list(self._backup_middle_timings[0])

        packet1 = self._build_packet(
                D=device,
                F=function,
                T=toggle
        )

        self._lead_out = self._backup_lead_out[:]

        packet2 = self._build_packet(
            D=device,
            F=function,
            T=toggle
        )

        self._lead_out = lead_out

        repeat = (
            self._repeat_lead_in[:] +
            self._repeat_bursts[1][:] +
            self._repeat_lead_out[:]
        )

        params = dict(
            frequency=self.frequency,
            D=device,
            F=function,
            T=toggle[:-2:]
        )

        code = protocol_base.IRCode(
            self,
            packet1[:] + packet2[:] + (repeat * repeat_count),
            [packet1[:], packet2[:]] + ([repeat] * repeat_count),
            params,
            repeat_count
        )

        return code
