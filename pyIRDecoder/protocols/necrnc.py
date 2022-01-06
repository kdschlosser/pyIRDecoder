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
from . import DecodeError


TIMING = 564


class NECrnc(protocol_base.IrProtocolBase):
    """
    IR decoder for the NECrnc protocol.
    """
    irp = (
        '{38.4k,564,lsb}<1,-1|1,-3>'
        '(16,-8,D:8,S:8,F:8,~F:4:4,~F:4,1,^108m,(16,-4,1,^108m)*)'
    )
    frequency = 38400
    bit_count = 32
    encoding = 'lsb'

    _lead_in = [TIMING * 16, -TIMING * 8]
    _lead_out = [TIMING, 108000]
    _middle_timings = []
    _bursts = [[TIMING, -TIMING], [TIMING, -TIMING * 3]]

    _repeat_lead_in = [TIMING * 16, -TIMING * 4]
    _repeat_lead_out = [TIMING, -96156]
    repeat_timeout = 108000

    _code_order = [
        ['D', 8],
        ['S', 8],
        ['F', 8],
    ]

    _parameters = [
        ['D', 0, 7],
        ['S', 8, 15],
        ['F', 16, 23],
        ['F2_CHECKSUM', 24, 27],
        ['F1_CHECKSUM', 28, 31]
    ]
    # [D:0..255,S:0..255=255-D,F:0..255]
    encode_parameters = [
        ['device', 0, 255],
        ['sub_device', 0, 255],
        ['function', 0, 255],
    ]

    @staticmethod
    def _calc_checksum(
        function: protocol_base.IntegerWrapper
    ) -> Sequence[protocol_base.IntegerWrapper]:
        return function[True:4:0], function[True:4:4]

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)
        f1_checksum, f2_checksum = self._calc_checksum(code.function)

        if (
            f1_checksum != code.f1_checksum or
            f2_checksum != code.f2_checksum
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
        sub_device: int,
        function: int,
        repeat_count: int = 0,
        use_repeat_frame: bool = True
    ) -> protocol_base.IRCode:
        function = protocol_base.IntegerWrapper(
            function,
            8,
            self._bursts,
            self.encoding
        )

        f1_checksum, f2_checksum = self._calc_checksum(function)
        params = dict(
            D=device,
            S=sub_device,
            F=function,
            F2_CHECKSUM=f2_checksum,
            F1_CHECKSUM=f1_checksum
        )

        packet = self._build_packet(**params)
        params['frequency'] = self.frequency

        if use_repeat_frame:
            repeat = self._repeat_lead_in[:] + self._repeat_lead_out[:]

            code = protocol_base.IRCode(
                self,
                packet[:] + (repeat[:] * repeat_count),
                [packet[:]] + ([repeat[:]] * repeat_count),
                params,
                repeat_count
            )
        else:
            code = protocol_base.IRCode(
                self,
                packet[:] * (repeat_count + 1),
                [packet[:]] * (repeat_count + 1),
                params,
                repeat_count
            )

        return code
