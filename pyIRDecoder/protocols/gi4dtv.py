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


TIMING = 992


class GI4DTV(protocol_base.IrProtocolBase):
    """
    IR decoder for the GI4DTV protocol.
    """
    irp = (
        '{37.3k,992,lsb}<1,-1|1,-3>'
        '(5,-2,F:6,D:2,C0:1,C1:1,C2:1,C3:1,1,-60)*'
        '{C0=D:1:2+#(F&25)+#(D&1),'
        'C1=D:1:2+#(F&43)+#(D&3),'
        'C2=D:1:2+#(F&22)+#(D&3),'
        'C3=D:1:2+#(F&44)+#(D&2)}'
    )
    frequency = 37300
    bit_count = 12
    encoding = 'lsb'

    _lead_in = [TIMING * 5, -TIMING * 2]
    _lead_out = [TIMING, -TIMING * 60]
    _middle_timings = []
    _bursts = [[TIMING, -TIMING], [TIMING, -TIMING * 3]]

    _code_order = [
        ['F', 6],
        ['D', 2]
    ]

    _parameters = [
        ['F', 0, 5],
        ['D', 6, 7],
        ['C0', 8, 8],
        ['C1', 9, 9],
        ['C2', 10, 10],
        ['C3', 11, 11]
    ]
    # [D:0..7,F:0..63]
    encode_parameters = [
        ['device', 0, 7],
        ['function', 0, 63],
    ]

    @classmethod
    def _calc_checksum(
        cls,
        device: protocol_base.IntegerWrapper,
        function: protocol_base.IntegerWrapper
    ) -> Sequence[protocol_base.IntegerWrapper]:

        c0 = (
            device[:1:2] + (function & 25).num_one_bits +
            (device & 1).num_one_bits
        )
        c1 = (
            device[:1:2] + (function & 43).num_one_bits +
            (device & 3).num_one_bits
        )
        c2 = (
            device[:1:2] + (function & 22).num_one_bits +
            (device & 3).num_one_bits
        )
        c3 = (
            device[:1:2] + (function & 44).num_one_bits +
            (device & 2).num_one_bits
        )

        return c0[:1:0], c1[:1:0], c2[:1:0], c3[:1:0]

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)
        c0, c1, c2, c3 = self._calc_checksum(code.device, code.function)

        if (c0, c1, c2, c3) != (code.c0, code.c1, code.c2, code.c3):
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
            2, 
            self._bursts, 
            self.encoding
        )
        function = protocol_base.IntegerWrapper(
            function, 
            6, 
            self._bursts, 
            self.encoding
        )
        c0, c1, c2, c3 = self._calc_checksum(device, function)

        params = dict(
            D=device,
            F=function,
            C0=c0,
            C1=c1,
            C2=c2,
            C3=c3
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
