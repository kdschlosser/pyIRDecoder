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


TIMING = 406


class DishNetwork(protocol_base.IrProtocolBase):
    """
    IR decoder for the Dish_Network protocol.
    """
    irp = '{57.6k,406,lsb}<1,-7|1,-4>(1,-15,(F:-6,S:5,D:5,1,-15)+)'
    frequency = 57600
    bit_count = 16
    encoding = 'lsb'

    _lead_in = [TIMING, -TIMING * 15]
    _lead_out = [TIMING, -TIMING * 15]
    _middle_timings = []
    _bursts = [[TIMING, -TIMING * 7], [TIMING, -TIMING * 4]]

    _code_order = [
        ['F', 6],
        ['S', 5],
        ['D', 5]
    ]

    _parameters = [
        ['F', 0, 5],
        ['S', 6, 10],
        ['D', 11, 15],
    ]
    # [F:0..63,S:0..31,D:0..31]
    encode_parameters = [
        ['device', 0, 31],
        ['sub_device', 0, 31],
        ['function', 0, 63]
    ]

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        self._lead_in = [TIMING, -TIMING * 15]

        try:
            code = protocol_base.IrProtocolBase.decode(self, data, frequency)
        except IRException:
            del self._lead_in[:]
            code = protocol_base.IrProtocolBase.decode(self, data, frequency)

        function = code.function[:-6:]

        params = dict(
            D=code.device,
            S=code.sub_device,
            F=function,
            frequency=self.frequency
        )

        code = protocol_base.IRCode(
            self,
            code.original_rlc,
            code.normalized_rlc,
            params
        )

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
        func = protocol_base.IntegerWrapper(
            function,
            6,
            self._bursts,
            self.encoding
        )[:-6:]
        lead_in = self._lead_in[:]

        self._lead_in = [TIMING, -TIMING * 15]
        packet = self._build_packet(
            F=func,
            S=sub_device,
            D=device,
        )
        del self._lead_in[:]
        repeat = self._build_packet(
            F=func,
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
