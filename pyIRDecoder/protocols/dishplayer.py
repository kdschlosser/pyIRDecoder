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
from . import IRException


TIMING = 535


class DishPlayer(protocol_base.IrProtocolBase):
    """
    IR decoder for the DishPlayer protocol.
    """
    irp = '{38.4k,535,msb}<1,-5|1,-3>(1,-11,(F:6,S:5,D:2,1,-11)+)'
    frequency = 38400
    bit_count = 13
    encoding = 'msb'

    _lead_in = [TIMING, -TIMING * 11]
    _lead_out = [TIMING, -TIMING * 11]
    _bursts = [[TIMING, -TIMING * 5], [TIMING, -TIMING * 3]]

    _code_order = [
        ['F', 6],
        ['S', 5],
        ['D', 2]
    ]

    _parameters = [
        ['F', 0, 5],
        ['S', 6, 10],
        ['D', 11, 12],
    ]
    # [F:0..63,S:0..31,D:0..3]
    encode_parameters = [
        ['device', 0, 3],
        ['sub_device', 0, 31],
        ['function', 0, 63]
    ]

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        self._lead_in = [TIMING, -TIMING * 11]
        
        try:
            code = protocol_base.IrProtocolBase.decode(self, data, frequency)
        except IRException:
            del self._lead_in[:]
            code = protocol_base.IrProtocolBase.decode(self, data, frequency)

        if self._last_code is not None:
            if self._last_code == code:
                return self._last_code

            self._last_code.repeat_timer.stop()

        self._last_code = code
        return code

    def encode(
            self,
            device: int,
            sub_device: int,
            function: int,
            repeat_count: int = 0
    ) -> protocol_base.IRCode:
        lead_in = self._lead_in[:]

        self._lead_in = [TIMING, -TIMING * 15]
        packet = self._build_packet(
            F=function,
            S=sub_device,
            D=device,
        )
        del self._lead_in[:]
        repeat = self._build_packet(
            F=function,
            S=sub_device,
            D=device,
        )

        self._lead_in = lead_in[:]

        params = dict(
            frequency=self.frequency,
            D=device,
            S=sub_device,
            F=function,
        )

        code = protocol_base.IRCode(
            self,
            packet[:] + (repeat * repeat_count),
            [packet[:]] + ([repeat] * repeat_count),
            params,
            repeat_count
        )
        return code
