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


TIMING = 106


class Metz19(protocol_base.IrProtocolBase):
    """
    IR decoder for the Metz19 protocol.
    """
    irp = (
        '{37.9k,106,msb}<4,-9|4,-16>'
        '(8,-22,(1-T):1,D:3,~D:3,F:6,~F:6,4,-125m)*'
    )
    frequency = 37900
    bit_count = 19
    encoding = 'msb'

    _lead_in = [TIMING * 8, -TIMING * 22]
    _lead_out = [TIMING * 4, -125000]
    _middle_timings = []
    _bursts = [[TIMING * 4, -TIMING * 9], [TIMING * 4, -TIMING * 16]]

    _code_order = [
        ['D', 3],
        ['F', 6],
    ]

    _current_toggle = 0

    _parameters = [
        ['T', 0, 0],
        ['D', 1, 3],
        ['D_CHECKSUM', 4, 6],
        ['F', 7, 12],
        ['F_CHECKSUM', 13, 18],
    ]

    # [D:0..7,F:0..63,T@:0..1=0]
    encode_parameters = [
        ['device', 0, 7],
        ['function', 0, 63]
    ]

    @staticmethod
    def _calc_checksum(
        device: protocol_base.IntegerWrapper,
        function: protocol_base.IntegerWrapper
    ) -> Sequence[protocol_base.IntegerWrapper]:
        return device[True:3:0], function[True:6:0]

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)

        dev_checksum, func_checksum = (
            self._calc_checksum(code.device, code.function)
        )

        if (
            dev_checksum != code.d_checksum or
            func_checksum != code.f_checksum
        ):
            raise DecodeError('Checksum failed')

        if self._last_code is not None:
            if (
                self._last_code == code and
                self._last_code.toggle == code.toggle
            ):
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
            3,
            self._bursts,
            self.encoding
        )
        function = protocol_base.IntegerWrapper(
            function,
            6,
            self._bursts,
            self.encoding
        )

        dev_checksum, func_checksum = (
            self._calc_checksum(device, function)
        )
        self._current_toggle = int(not self._current_toggle)

        params = dict(
            D=device,
            F=function,
            T=self._current_toggle,
            D_CHECKSUM=dev_checksum,
            F_CHECKSUM=func_checksum
        )

        packet = self._build_packet(**params)

        params['frequency'] = self.frequency

        code = protocol_base.IRCode(
            self,
            packet[:] * (repeat_count + 1),
            [packet[:]] * (repeat_count + 1),
            params,
            repeat_count
        )

        return code
