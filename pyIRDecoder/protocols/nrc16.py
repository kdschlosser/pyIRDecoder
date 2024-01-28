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
    IRException,
    DecodeError,
    RepeatLeadInError,
    RepeatLeadOutError,
    ExpectingMoreData
)


TIMING = 500


class NRC16(protocol_base.IrProtocolBase):
    """
    IR decoder for the NRC16 protocol.
    """
    irp = (
        '{38k,500}<-1,1|1,-1>(1,-5,1:1,254:8,127:7,-15m,(1,-5,1:1,F:8,D:7,-110m)+,1,-5,1:1,254:8,127:7,-15m)'
    )

    frequency = 38000
    bit_count = 48
    encoding = 'lsb'

    _lead_in = [TIMING, -TIMING * 5]
    _lead_out = []
    _lead_out1 = [-15000]
    _lead_out2 = [-110000]
    _bursts = [[-TIMING, TIMING], [TIMING, -TIMING]]

    _has_repeat_lead_out = True

    _code_order = [
        ['F', 8],
        ['D', 7]
    ]

    _parameters = [
        ['C', 0, 0],
        ['F', 1, 8],
        ['D', 9, 15]
    ]

    # [D:0..127,F:0..255]
    encode_parameters = [
        ['device', 0, 127],
        ['function', 0, 255],
    ]

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        '1,-5,1:1,254:8,127:7,-15m'
        '1,-5,1:1,F:8,D:7,-110m'
        '1,-5,1:1,254:8,127:7,-15m'

        codes = []
        code = []
        for item in data:
            code.append(item)
            if item > 0:
                continue

            if (
                self._match(item, self._lead_out1[0]) or
                self._match(item, self._bursts[-1][-1] + self._lead_out1[0])
            ):
                self._lead_out = self._lead_out1[:]
                self.bit_count = 16

                try:
                    code = protocol_base.IrProtocolBase.decode(self, code, frequency)
                except:
                    self._lead_out =[]
                    self.bit_count = 48
                    raise

                if (
                    code.checksum != 1 or
                    code.function != 254 or
                    code.device != 127
                ):
                    raise DecodeError
                codes.append(code)
                code = []

            elif (
                self._match(item, self._lead_out2[0]) or
                self._match(item, self._bursts[-1][-1] + self._lead_out2[0])
            ):

                self._lead_out = self._lead_out2[:]
                self.bit_count = 16

                try:
                    code = protocol_base.IrProtocolBase.decode(
                        self,
                        code,
                        frequency
                        )
                except:
                    self._lead_out = []
                    self.bit_count = 48
                    raise

                codes.append(code)
                code = []

        if not codes:
            raise DecodeError

        if len(codes) == 1 and len(self._stored_codes) == 3:
            code = codes[0]

            if self._last_code is not None:
                if (
                    code.function == self._last_code.function and
                    code.device == self._last_code.device
                ):
                    return self._last_code

                self._last_code.repeat_timer.stop()

                self._last_code = None

            del self._stored_codes[:]
            self._stored_codes.append(code)
            raise ExpectingMoreData

        if len(self._stored_codes) == 3:
            del self._stored_codes[:]

        for code in codes:
            self._stored_codes.append(code)

        if len(self._stored_codes) == 3:
            code1, code2, code3 = self._stored_codes

            if (
                code1.checksum == 1 == code3.checksum and
                code1.function == 254 == code3.function and
                code1.device == 127 == code3.device
            ):

                code = code1 + code2 + code3

            if self._last_code is not None:
                self._last_code.repeat_timer.stop()
                self._last_code = None

            self._last_code = code

            return code
        raise ExpectingMoreData

    def encode(
        self,
        device: int,
        function: int,
        repeat_count: int = 0
    ) -> protocol_base.IRCode:

        self.__class__._lead_out = self._lead_out1[:]
        prefix = suffix = self._build_packet(D=127, F=254, C=1)

        self.__class__._lead_out = self._lead_out2[:]
        packet = self._build_packet(D=device, F=function, C=1)

        params = dict(
            frequency=self.frequency,
            D=device,
            F=function,
            C=1
        )

        code = protocol_base.IRCode(
            self,
            prefix[:] + packet[:] + suffix[:] + (packet[:] * repeat_count),
            [prefix[:]] + [packet[:]] + [suffix[:]] + ([packet[:]] * repeat_count),
            params,
            repeat_count
        )

        return code
