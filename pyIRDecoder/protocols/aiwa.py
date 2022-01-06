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

TIMING = 550


class Aiwa(protocol_base.IrProtocolBase):
    """
    IR decoder for the Aiwa protocol.
    """
    irp = (
        '{38.123k,550,lsb}<1,-1|1,-3>(16,-8,D:8,S:5,~D:8,~S:5,F:8,~F:8,1,-42,'
        '(16,-8,1,-165)*)'
    )
    frequency = 38123
    bit_count = 42
    encoding = 'lsb'

    _lead_in = [TIMING * 16, -TIMING * 8]
    _lead_out = [TIMING, -TIMING * 42]
    _bursts = [[TIMING, -TIMING], [TIMING, -TIMING * 3]]

    _repeat_lead_in = [TIMING * 16, -TIMING * 8]
    _repeat_lead_out = [TIMING, -TIMING * 165]

    _code_order = [
        ['D', 8],
        ['S', 5],
        ['F', 8]
    ]

    _parameters = [
        ['D', 0, 7],
        ['S', 8, 12],
        ['D_CHECKSUM', 13, 20],
        ['S_CHECKSUM', 21, 25],
        ['F', 26, 33],
        ['F_CHECKSUM', 34, 41],
    ]
    # [D:0..255,S:0..31,F:0..255]
    encode_parameters = [
        ['device', 0, 255],
        ['sub_device', 0, 31],
        ['function', 0, 255],
    ]

    @staticmethod
    def _calc_checksum(
        device: protocol_base.IntegerWrapper,
        sub_device: protocol_base.IntegerWrapper,
        function: protocol_base.IntegerWrapper
    ) -> Sequence[protocol_base.IntegerWrapper]:

        d = device[True::]
        s = sub_device[True::]
        f = function[True::]

        return d, s, f

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)
        if self._last_code is not None:
            if self._last_code == code:
                return self._last_code

            self._last_code.repeat_timer.stop()

        (
            device_checksum,
            sub_checksum,
            func_checksum
        ) = self._calc_checksum(code.device, code.sub_device, code.function)

        if (
            device_checksum != code.d_checksum or
            sub_checksum != code.s_checksum or
            func_checksum != code.f_checksum
        ):
            raise DecodeError('Checksum failed')

        self._last_code = code
        return code

    def encode(self, device, sub_device, function, repeat_count=0):
        device = protocol_base.IntegerWrapper(
            device,
            8,
            self._bursts,
            self.encoding
        )
        sub_device = protocol_base.IntegerWrapper(
            sub_device,
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

        dev_checksum, sub_checksum, func_checksum = (
            self._calc_checksum(device, sub_device, function)
        )

        packet = self._build_packet(
            D=device,
            S=sub_device,
            D_CHECKSUM=dev_checksum,
            S_CHECKSUM=sub_checksum,
            F=function,
            F_CHECKSUM=func_checksum,
        )

        params = dict(
            frequency=self.frequency,
            D=device,
            S=sub_device,
            F=function
        )

        if repeat_count:
            repeat = self._repeat_lead_in[:] + self._repeat_lead_out[:]

            code = protocol_base.IRCode(
                self,
                packet[:] + (repeat * repeat_count),
                [packet[:]] + ([repeat[:]] * repeat_count),
                params,
                repeat_count
            )
        else:
            code = protocol_base.IRCode(
                self,
                packet[:],
                [packet[:]],
                params,
                repeat_count
            )

        return code
