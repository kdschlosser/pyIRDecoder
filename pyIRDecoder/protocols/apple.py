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


TIMING = 564


class Apple(protocol_base.IrProtocolBase):
    """
    IR decoder for the Apple protocol.
    """
    irp = (
        '{38.4k,564,lsb}<1,-1|1,-3>'
        '(16,-8,D:8,S:8,C:1,F:7,PairID:8,1,^108m,(16,-4,1,^108m)*)'
        '{C=1-(#F+#PairID)%2,S=135}'
    )
    frequency = 38400
    bit_count = 32
    encoding = 'lsb'

    _lead_in = [TIMING * 16, -TIMING * 8]
    _lead_out = [TIMING, 108000]
    _bursts = [[TIMING, -TIMING], [TIMING, -TIMING * 3]]

    _repeat_lead_in = [TIMING * 16, -TIMING * 4]
    _repeat_lead_out = [TIMING, 108000]

    _code_order = [
        ['D', 8],
        ['F', 7],
        ['PAIR_ID', 8]
    ]

    _parameters = [
        ['D', 0, 7],
        ['S', 8, 15],
        ['CHECKSUM', 16, 16],
        ['F', 17, 23],
        ['PAIR_ID', 24, 31]
    ]
    # [D:0..255=238,F:0..127,PairID:0..255]
    encode_parameters = [
        ['device', 0, 255],
        ['function', 0, 127],
        ['pair_id', 0, 255]
    ]

    @staticmethod
    def _calc_checksum(
        function: protocol_base.IntegerWrapper,
        pair_id: protocol_base.IntegerWrapper
    ) -> protocol_base.IntegerWrapper:
        c = 1 - (
            function.num_one_bits +
            pair_id.num_one_bits
        ) % 2
        return c

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)

        if self._last_code is not None:
            if self._last_code == code:
                return self._last_code

            self._last_code.repeat_timer.stop()

        checksum = self._calc_checksum(code.function, code.pair_id)

        if code.sub_device != 135 or checksum != code.checksum:
            raise DecodeError('Checksum failed')

        self._last_code = code
        return code

    def encode(
        self,
        device: int,
        function: int,
        pair_id: int,
        repeat_count: int = 0
    ) -> protocol_base.IRCode:
        function = protocol_base.IntegerWrapper(
            function,
            7,
            self._bursts,
            self.encoding
        )
        pair_id = protocol_base.IntegerWrapper(
            pair_id,
            8,
            self._bursts,
            self.encoding
        )

        checksum = self._calc_checksum(function, pair_id)

        packet = self._build_packet(
                D=device,
                S=135,
                CHECKSUM=checksum,
                F=function,
                PAIR_ID=pair_id
        )

        params = dict(
            frequency=self.frequency,
            D=device,
            F=function,
            PAIR_ID=pair_id
        )

        repeat = self._build_repeat_packet(repeat_count)

        code = protocol_base.IRCode(
            self,
            packet[:] + repeat,
            [packet[:]] + repeat,
            params,
            repeat_count
        )
        return code
