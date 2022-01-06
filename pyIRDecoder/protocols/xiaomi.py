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

TIMING = 290


class Xiaomi(protocol_base.IrProtocolBase):
    """
    IR decoder for the Grundig16 protocol.
    """
    irp = (
        '{36k,290,msb}<2,-2|2,-3|2,-4|2,-5>'
        '(1000u,-2,D:8,F:8,C:4,2,^30m)* '
        '{C=(D:4:4^D:4^F:4:4^F:4)}'
    )
    frequency = 36000
    bit_count = 20
    encoding = 'msb'

    _lead_in = [1000, -TIMING * 2]
    _lead_out = [TIMING * 2, 30000]
    _middle_timings = []
    _bursts = [
        [TIMING * 2, -TIMING * 2],
        [TIMING * 2, -TIMING * 3],
        [TIMING * 2, -TIMING * 4],
        [TIMING * 2, -TIMING * 5],
    ]

    _code_order = [
        ['D', 8],
        ['F', 8],
    ]
    _parameters = [
        ['D', 0, 7],
        ['F', 8, 15],
        ['CHECKSUM', 16, 19],
    ]
    # [D:0..255,F:0..255]
    encode_parameters = [
        ['device', 0, 255],
        ['function', 0, 255],
    ]

    @staticmethod
    def _calc_checksum(
        device: protocol_base.IntegerWrapper,
        function: protocol_base.IntegerWrapper
    ) -> protocol_base.IntegerWrapper:
        # {C=(D:4:4^D:4^F:4:4^F:4)}
        return device[:4:4] ^ device[:4:0] ^ function[:4:4] ^ function[:4:0]

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)

        checksum = self._calc_checksum(code.device, code.function)
        if checksum != code.checksum:
            raise DecodeError('Invalid checksum')

        if self._last_code is not None:
            if self._last_code == code:
                return self._last_code

            self._last_code.repeat_timer.stop()

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

        checksum = self._calc_checksum(device, function)

        params = dict(
            D=device,
            F=function,
            CHECKSUM=checksum
        )

        packet = self._build_packet(**params)
        params['frequncy'] = self.frequency

        code = protocol_base.IRCode(
            self,
            packet[:] * (repeat_count + 1),
            [packet[:]] * (repeat_count + 1),
            params,
            repeat_count
        )
        return code
