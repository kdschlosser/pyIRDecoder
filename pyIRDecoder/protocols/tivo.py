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


class Tivo(protocol_base.IrProtocolBase):
    """
    IR decoder for the Tivo protocol.
    """
    irp = (
        '{38.4k,564,lsb}<1,-1|1,-3>(16,-8,D:8,S:8,F:8,U:4,~F:4:4,1,-78,'
        '(16,-4,1,-173)*)'
    )
    frequency = 38400
    bit_count = 32
    encoding = 'lsb'

    _lead_in = [TIMING * 16, -TIMING * 8]
    _lead_out = [TIMING, -TIMING * 78]
    _middle_timings = []
    _bursts = [[TIMING, -TIMING], [TIMING, -TIMING * 3]]

    _repeat_lead_in = [TIMING * 16, -TIMING * 4]
    _repeat_lead_out = [TIMING, -TIMING * 173]

    _code_order = [
        ['F', 8],
        ['E', 4]
    ]

    _parameters = [
        ['D', 0, 7],
        ['S', 8, 15],
        ['F', 16, 23],
        ['E', 24, 27],
        ['CHECKSUM', 28, 31]
    ]
    # [D:133..133=133,S:48..48=48,F:0..255,U:0..15]
    encode_parameters = [
        ['function', 0, 255],
        ['extended_function', 0, 15]
    ]

    @staticmethod
    def _calc_checksum(
        function: protocol_base.IntegerWrapper
    ) -> protocol_base.IntegerWrapper:
        return function[True:4:4]

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        code = data[:]
        if len(code) == 4:
            in_mark, in_space, out_mark, out_space = code
            if (
                    self._match(in_mark, self._repeat_lead_in[0]) and
                    self._match(in_space, self._repeat_lead_in[1]) and
                    self._match(out_mark, self._repeat_lead_out[0]) and
                    self._match(out_space, self._repeat_lead_out[1])
            ):
                if self._last_code is None:
                    raise DecodeError('Invalid repeat sequence')

                return self._last_code

        code = protocol_base.IrProtocolBase.decode(self, data, frequency)
        checksum = self._calc_checksum(code.function)

        if (
            checksum != code.checksum or
            code.device != 133 or
            code.sub_device != 48
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
        function: int,
        extended_function: int,
        repeat_count: int = 0
    ) -> protocol_base.IRCode:
        function = protocol_base.IntegerWrapper(
            function,
            8,
            self._bursts,
            self.encoding
        )
        checksum = self._calc_checksum(function)
        params = dict(
            E=extended_function,
            F=function,
            D=133,
            S=48,
            CHECKSUM=checksum
        )

        packet = self._build_packet(**params)

        params['frequency'] = self.frequency

        repeat = self._repeat_lead_in[:] + self._repeat_lead_out[:]

        code = protocol_base.IRCode(
            self,
            packet[:] + (repeat[:] * repeat_count),
            [packet[:]] + ([repeat[:]] * repeat_count),
            params,
            repeat_count
        )

        return code
