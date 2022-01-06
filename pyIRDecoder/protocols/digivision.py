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


TIMING = 182


class Digivision(protocol_base.IrProtocolBase):
    """
    IR decoder for the Digivision protocol.
    """
    irp = (
        '{38.0k,182,lsb}<3,-3|3,-6>'
        '(20,-10,D:8,Dev2:8,Dev3:8,20,-10,F:8,~F:8,3,^108m,(20,-20,3,^108m)*)'
    )
    frequency = 38400
    bit_count = 40
    encoding = 'lsb'

    _lead_in = [TIMING * 20, -TIMING * 10]
    _lead_out = [TIMING * 3, 108000]
    _middle_timings = [(TIMING * 20, -TIMING * 10)]
    _bursts = [[TIMING * 3, -TIMING * 3], [TIMING * 3, -TIMING * 6]]

    _repeat_lead_in = [TIMING * 20, -TIMING * 20]
    _repeat_lead_out = [TIMING * 3, 108000]

    _code_order = [
        ['D', 8],
        ['DEVICE2', 8],
        ['DEVICE3', 8],
        ['F', 8]
    ]

    _parameters = [
        ['D', 0, 7],
        ['DEVICE2', 8, 15],
        ['DEVICE3', 16, 23],
        ['F', 24, 31],
        ['F_CHECKSUM', 32, 39]
    ]
    # [D:0..255,Dev2:0..255,Dev3:0..255,F:0..255]
    encode_parameters = [
        ['device', 0, 255],
        ['device2', 0, 255],
        ['device3', 0, 255],
        ['function', 0, 255]
    ]

    @staticmethod
    def _calc_checksum(
        function: protocol_base.IntegerWrapper
    ) -> protocol_base.IntegerWrapper:
        return function[True:8:0]

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)
        func_checksum = self._calc_checksum(code.function)

        if func_checksum != code.f_checksum:
            raise DecodeError('Checksum failed')

        if self._last_code is not None:
            if self._last_code == code:
                return self._last_code

            self._last_code.repeat_timer.stop()

        self._last_code = code
        return code

    def encode(
        self,
        device: int,
        device2: int,
        device3: int,
        function: int,
        repeat_count: int = 0
    ) -> protocol_base.IRCode:
        device = protocol_base.IntegerWrapper(
            device,
            8,
            self._bursts,
            self.encoding
        )
        device2 = protocol_base.IntegerWrapper(
            device2,
            8,
            self._bursts,
            self.encoding
        )
        device3 = protocol_base.IntegerWrapper(
            device3,
            8,
            self._bursts,
            self.encoding
        )
        function = protocol_base.IntegerWrapper(
            function,
            8,
            self._bursts,
            self.encoding
        )

        func_checksum = self._calc_checksum(function)

        packet = self._build_packet(
            device.timings,
            device2.timings,
            device3.timings,
            self._middle_timings[0],
            function.timings,
            func_checksum.timings,
        )

        params = dict(
            frequency=self.frequency,
            D=device,
            DEVICE2=device2,
            DEVICE3=device3,
            F=function,
        )

        repeat = self._build_repeat_packet(repeat_count)

        code = protocol_base.IRCode(
            self,
            packet[:] + [item for items in repeat for item in items],
            [packet[:]] + repeat,
            params,
            repeat_count
        )

        return code
