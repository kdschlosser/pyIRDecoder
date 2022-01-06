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
    LeadOutError,
    RepeatLeadInError
)


TIMING = 512


class Blaupunkt(protocol_base.IrProtocolBase):
    """
    IR decoder for the Blaupunkt protocol.
    """
    irp = (
        '{30.3k,512,lsb}<-1,1|1,-1>'
        '(1,-5,1023:10,-44,'
        '(1,-5,1:1,F:6,D:3,-236)+'
        ',1,-5,1023:10,-44)'
    )
    frequency = 30300
    bit_count = 10
    encoding = 'lsb'

    _lead_in = [TIMING, -TIMING * 5]
    _lead_out1 = [-TIMING * 44]  # 22528
    _lead_out2 = [-TIMING * 236]  # 120832

    _bursts = [[-TIMING, TIMING], [TIMING, -TIMING]]

    _code_order = [
        ['F', 6],
        ['D', 3]
    ]

    _parameters = [
        ['C0', 0, 0],
        ['F', 1, 6],
        ['D', 7, 9]
    ]
    # [F:0..63,D:0..7]
    encode_parameters = [
        ['device', 0, 7],
        ['function', 0, 63],
    ]

    _has_repeat_lead_out = True

    repeat_timeout = (
        (bit_count * sum(abs(item) for item in _bursts[0])) +
        sum(abs(item) for item in _lead_in) + abs(_lead_out2[0])
    )

    _saved_codes = []

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        self._lead_out = self._lead_out1

        try:
            code = protocol_base.IrProtocolBase.decode(self, data, frequency)
            if code.c0 != 1:
                del self._saved_codes[:]
                raise DecodeError
            if code.device != 7:
                del self._saved_codes[:]
                raise DecodeError
            if code.function != 63:
                del self._saved_codes[:]
                raise DecodeError

            if len(self._saved_codes) == 2:
                device = self._last_code.device
                function = self._last_code.function

                del self._saved_codes[:]
                self._last_code += code
                # noinspection PyProtectedMember
                self._last_code._data['F'] = function
                # noinspection PyProtectedMember
                self._last_code._data['D'] = device
                raise RepeatLeadOutError

            elif not self._saved_codes:
                self._saved_codes.append(code)
                raise RepeatLeadInError
            else:
                del self._daved_codes[:]
                raise DecodeError
        except LeadOutError:
            self._lead_out = self._lead_out2
            code = protocol_base.IrProtocolBase.decode(self, data, frequency)

            if code.c0 != 1:
                del self._saved_codes[:]
                raise DecodeError

            if len(self._saved_codes) == 1:
                code += self._saved_codes[0]
                self._saved_codes.append(code)

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

        packet = self._build_packet(
            C0=1,
            D=device,
            F=function
        )

        if packet[-1] < 0:
            packet[-1] += self._lead_out2[0]
        else:
            packet.extend(self._lead_out2)

        lead = self._build_packet(
            C0=1,
            D=7,
            F=63
        )

        if lead[-1] < 0:
            lead[-1] += self._lead_out1[0]
        else:
            lead.extend(self._lead_out1)

        params = dict(
            frequency=self.frequency,
            D=device,
            F=function,
        )

        code = protocol_base.IRCode(
            self,
            lead[:] + (packet * (repeat_count + 1)) + lead[:],
            [lead[:]] + ([packet] * (repeat_count + 1)) + [lead[:]],
            params,
            repeat_count
        )
        return code
