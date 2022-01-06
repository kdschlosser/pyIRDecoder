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


class Somfy(protocol_base.IrProtocolBase):
    """
    IR decoder for the Somfy protocol.
    """
    irp = (
        '{35.7k,1,lsb}<308,-881|669,-520>'
        '(2072,-484,F:2,D:3,C:4,-2300)*'
        '{C=F*4+D+3}'
    )
    frequency = 35700
    bit_count = 9
    encoding = 'lsb'

    _lead_in = [2072, -484]
    _lead_out = [-2300]
    _middle_timings = []
    _bursts = [[308, -881], [669, -520]]

    _code_order = [
        ['F', 2],
        ['D', 3],
    ]

    _parameters = [
        ['F', 0, 1],
        ['D', 2, 4],
        ['CHECKSUM', 5, 8]
    ]
    # [F:0..3,D:0..7]
    encode_parameters = [
        ['device', 0, 7],
        ['function', 0, 3],
    ]

    @staticmethod
    def _calc_checksum(
        device: protocol_base.IntegerWrapper,
        function: protocol_base.IntegerWrapper
    ) -> protocol_base.IntegerWrapper:
        # {C=F*4+D+3}
        return (function * 4 + device + 3)[:4:0]

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)

        checksum = self._calc_checksum(code.device, code.function)
        if checksum != code.checksum:
            raise DecodeError('Checksum failed')

        if self._last_code is not None:
            if self._last_code == code:
                return self._last_code

            self._last_code.refresh_timer.stop()
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
            2,
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

        params['frequency'] = self.frequency

        code = protocol_base.IRCode(
            self,
            packet[:] * (repeat_count + 1),
            [packet[:]] * (repeat_count + 1),
            params,
            repeat_count
        )

        return code
