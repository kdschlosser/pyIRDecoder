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
    RepeatLeadInError,
    RepeatLeadOutError,
    IRException,
    ExpectingMoreData
)


TIMING = 500


class NRC17(protocol_base.IrProtocolBase):
    """
    IR decoder for the NRC17 protocol.
    """
    irp = (
        '{500,38k,25%}<-1,1|1,-1>'
        '(1,-5,1:1,254:8,255:8,-28, '
        '(1,-5,1:1,F:8,D:8,-220)*, '
        '1,-5,1:1,254:8,255:8,-200)'
    )
    frequency = 38000
    bit_count = 17
    encoding = 'lsb'

    _lead_in = [TIMING, -TIMING * 5]
    _lead_out = []
    _lead_out1 = [-TIMING * 28]
    _lead_out2 = [-TIMING * 220]
    _lead_out3 = [-TIMING * 200]
    _middle_timings = []
    _bursts = [[-TIMING, TIMING], [TIMING, -TIMING]]

    _code_order = [
        ['F', 8],
        ['D', 8],
    ]

    _parameters = [
        ['C', 0, 0],
        ['F', 1, 8],
        ['D', 9, 16]
    ]
    # [D:0..255,F:0..255]
    encode_parameters = [
        ['device', 0, 255],
        ['function', 0, 255],
    ]

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        tolerance = self.tolerance
        self.tolerance = 5
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
                self.bit_count = 17

                try:
                    code = protocol_base.IrProtocolBase.decode(
                        self,
                        code,
                        frequency
                        )
                except:
                    self._lead_out = []
                    self.bit_count = 51
                    self.tolerance = tolerance
                    raise

                if (
                    code.checksum != 1 or
                    code.function != 254 or
                    code.device != 255
                ):
                    self._lead_out = []
                    self.bit_count = 17
                    self.tolerance = tolerance
                    raise DecodeError

                codes.append(code)
                code = []

            elif (
                self._match(item, self._lead_out2[0]) or
                self._match(item, self._bursts[-1][-1] + self._lead_out2[0])
            ):

                self._lead_out = self._lead_out2[:]
                self.bit_count = 17

                try:
                    code = protocol_base.IrProtocolBase.decode(
                        self,
                        code,
                        frequency
                    )
                except:
                    self._lead_out = []
                    self.bit_count = 51
                    self.tolerance = tolerance
                    raise

                codes.append(code)
                code = []

            elif (
                self._match(item, self._lead_out3[0]) or
                self._match(item, self._bursts[-1][-1] + self._lead_out3[0])
            ):

                self._lead_out = self._lead_out3[:]
                self.bit_count = 17

                try:
                    code = protocol_base.IrProtocolBase.decode(
                        self,
                        code,
                        frequency
                    )
                except:
                    self._lead_out = []
                    self.bit_count = 51
                    self.tolerance = tolerance
                    raise

                if (
                    code.checksum != 1 or
                    code.function != 254 or
                    code.device != 255
                ):
                    self._lead_out = []
                    self.bit_count = 51
                    self.tolerance = tolerance
                    raise DecodeError

                codes.append(code)
                code = []

        if not codes:
            self._lead_out = []
            self.bit_count = 51
            self.tolerance = tolerance

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
            self._lead_out = []
            self.bit_count = 51
            self.tolerance = tolerance
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
                code1.device == 255 == code3.device
            ):

                code = code1 + code2 + code3

            if self._last_code is not None:
                self._last_code.repeat_timer.stop()
                self._last_code = None

            self._last_code = code

            return code

        self.tolerance = tolerance
        raise ExpectingMoreData

    def encode(
        self,
        device: int,
        function: int,
        repeat_count: int = 0
    ):

        params = dict(
            D=255,
            F=254,
            C=1
        )

        self.__class__._lead_out = self._lead_out1[:]
        prefix = self._build_packet(**params)

        self.__class__._lead_out = self._lead_out3[:]
        suffix = self._build_packet(**params)

        params['D'] = device
        params['F'] = function

        self.__class__._lead_out = self._lead_out2[:]
        packet = self._build_packet(**params)

        params['frequency'] = self.frequency

        code = protocol_base.IRCode(
            self,
            prefix[:] + packet[:] + suffix[:] + (packet[:] * repeat_count),
            [prefix[:]] + [packet[:]] + [suffix[:]] + ([packet[:]] * repeat_count),
            params,
            repeat_count
        )

        return code
