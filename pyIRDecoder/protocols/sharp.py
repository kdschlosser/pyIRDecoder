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
from . import DecodeError, IRException, RepeatLeadInError


TIMING = 264


class Sharp(protocol_base.IrProtocolBase):
    """
    IR decoder for the Sharp protocol.
    """
    irp = '{38k,264,lsb}<1,-3|1,-7>(D:5,F:8,1:2,1,-165,D:5,~F:8,2:2,1,-165)*'
    frequency = 38000
    bit_count = 30
    encoding = 'lsb'

    _lead_in = []
    _lead_out = [TIMING,  -TIMING * 165]
    _middle_timings = [(TIMING,  -TIMING * 165)]
    _bursts = [[TIMING, -TIMING * 3], [TIMING, -TIMING * 7]]

    _code_order = [
        ['D', 5],
        ['F', 8],
    ]

    _parameters1 = [
        ['D', 0, 4],
        ['F', 5, 12],
        ['C0', 13, 14]
    ]

    _parameters2 = [
        ['D', 0, 4],
        ['F', 5, 12],
        ['C0', 13, 14],
        ['D_CHECKSUM', 15, 19],
        ['F_CHECKSUM', 20, 27],
        ['C1', 28, 29]
    ]
    # [D:0..31,F:0..255]
    encode_parameters = [
        ['device', 0, 31],
        ['function', 0, 255],
    ]

    _partial_code = None

    @staticmethod
    def _calc_checksum(
        function: protocol_base.IntegerWrapper
    ) -> protocol_base.IntegerWrapper:
        return function[True:8:0]

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        self._parameters = self._parameters1

        try:
            code = protocol_base.IrProtocolBase.decode(self, data, frequency)

            if code.c0 == 1:
                self._partial_code = data[:]
                raise RepeatLeadInError

            if code.c0 != 2 or self._partial_code is None:
                self._partial_code = None
                raise DecodeError('Invalid ir stream')

            data = self._partial_code + data[:]
            self._partial_code = None
            self._parameters = self._parameters2
            code = protocol_base.IrProtocolBase.decode(self, data, frequency)

        except IRException:
            self._parameters = self._parameters2
            code = protocol_base.IrProtocolBase.decode(self, data, frequency)

        if code.c0 != 1 or code.c1 != 2:
            raise DecodeError('Checksum failed')

        f_checksum = self._calc_checksum(code.function)

        if (
            code.device != code.d_checksum or
            f_checksum != code.f_checksum
        ):
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
        repeat_count: int = 0
    ) -> protocol_base.IRCode:
        device = protocol_base.IntegerWrapper(
            device,
            5,
            self._bursts,
            self.encoding
        )
        function = protocol_base.IntegerWrapper(
            function,
            8,
            self._bursts,
            self.encoding
        )
        c0 = protocol_base.IntegerWrapper(
            1,
            2,
            self._bursts,
            self.encoding
        )
        c1 = protocol_base.IntegerWrapper(
            2,
            2,
            self._bursts,
            self.encoding
        )

        func_checksum = self._calc_checksum(function)

        packet = self._build_packet(
            device.timings,
            function.timings,
            c0.timings,
            self._middle_timings,
            device.timings,
            func_checksum.timings,
            c1.timings
        )

        params = dict(
            frequency=self.frequency,
            D=device,
            F=function,
        )

        code = protocol_base.IRCode(
            self,
            packet[:] * (repeat_count + 1),
            [packet[:]] * (repeat_count + 1),
            params,
            repeat_count
        )

        return code
