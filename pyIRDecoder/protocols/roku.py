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
from . import DecodeError, RepeatLeadInError


TIMING = 564


class Roku(protocol_base.IrProtocolBase):
    """
    IR decoder for the Roku protocol.
    """
    irp = (
        '{38.0k,564,lsb}<1,-1|1,-3>'
        '(16,-8,D:8,S:8,F:7,0:1,~F:7,1:1,1,^108m,'
        '(16,-8,D:8,S:8,F:7,1:1,~F:7,0:1,1,^108m)*)'
    )
    frequency = 38000
    bit_count = 32
    encoding = 'lsb'

    _lead_in = [TIMING * 16, -TIMING * 8]
    _lead_out = [TIMING, 108000]
    _middle_timings = []
    _bursts = [[TIMING, -TIMING], [TIMING, -TIMING * 3]]

    _code_order = [
        ['D', 8],
        ['S', 8],
        ['F', 7],
    ]

    _parameters = [
        ['D', 0, 7],
        ['S', 8, 15],
        ['F', 16, 22],
        ['T', 23, 23],
        ['F_CHECKSUM', 24, 30],
        ['T1', 31, 31]
    ]
    # [D:0..255,S:0..255=255-D,F:0..127]
    encode_parameters = [
        ['device', 0, 255],
        ['sub_device', 0, 255],
        ['function', 0, 127],
    ]

    @staticmethod
    def _calc_checksum(
        function: protocol_base.IntegerWrapper
    ) -> protocol_base.IntegerWrapper:
        return function[True:7:0]

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)
        func_checksum = self._calc_checksum(code.function)

        if func_checksum != code.f_checksum:
            raise DecodeError('Checksum failed')

        if code.toggle[True:1:0] != code.t1:
            raise DecodeError('Checksum failed')

        if self._last_code is not None:
            if self._last_code != code:
                pass
            elif (
                self._last_code.toggle == code.toggle or
                (
                    self._last_code.toggle == code.t1 and
                    self._last_code.t1 == code.toggle
                )
            ):
                return self._last_code

            self._last_code.repeat_timer.stop()

        self._last_code = code

        if not code.toggle:
            raise RepeatLeadInError

        return code

    def encode(
        self,
        device: int,
        sub_device: int,
        function: int,
        repeat_count: int = 0
    ) -> protocol_base.IRCode:
        function = protocol_base.IntegerWrapper(
            function,
            7,
            self._bursts,
            self.encoding
        )

        func_checksum = self._calc_checksum(function)

        params = dict(
            D=device,
            S=sub_device,
            F=function,
            F_CHECKSUM=func_checksum,
            T=0,
            T1=1
        )

        packet = self._build_packet(**params)

        params['T'] = 1
        params['T1'] = 0

        repeat = self._build_packet(**params)

        params['frequency'] = self.frequency

        code = protocol_base.IRCode(
            self,
            packet[:] + (repeat[:] * repeat_count),
            [packet[:]] + ([repeat[:]] * repeat_count),
            params,
            repeat_count
        )

        return code
