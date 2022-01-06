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

# *****************************************************************************

# Local imports
from . import protocol_base
from . import DecodeError, RepeatLeadInError

TIMING = 422


class F12(protocol_base.IrProtocolBase):
    """
    IR decoder for the F12 protocol.
    """
    irp = '{37.9k,422,lsb}<1,-3|3,-1>((D:3,S:1,F:8,-80)2)*'
    frequency = 37900
    bit_count = 12
    encoding = 'lsb'

    _lead_in = []
    _lead_out = [-TIMING * 80]
    _middle_timings = []
    _bursts = [[TIMING, -TIMING * 3], [TIMING * 3, -TIMING]]

    _repeat_lead_in = []
    _repeat_lead_out = []
    _repeat_bursts = []
    repeat_timeout = (
        (sum(abs(item) for item in _bursts[0]) * 12) + abs(_lead_out[0])
    ) * 2

    _code_order = [
        ['D', 3],
        ['S', 1],
        ['F', 8]
    ]

    _parameters = [
        ['D', 0, 2],
        ['S', 3, 3],
        ['F', 4, 11],
    ]
    # [D:0..7,S:0..1,F:0..255]
    encode_parameters = [
        ['device', 0, 7],
        ['sub_device', 0, 1],
        ['function', 0, 255],
    ]

    _saved_code = None

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)

        if self._saved_code is None:
            self._saved_code = code
            raise RepeatLeadInError

        if code != self._saved_code:
            raise DecodeError

        code = self._saved_code + code

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
        sub_device: int,
        function: int,
        repeat_count: int = 0
    ) -> protocol_base.IRCode:
        packet = self._build_packet(
            D=device,
            S=sub_device,
            F=function
        )

        params = dict(
            frequency=self.frequency,
            D=device,
            S=sub_device,
            F=function,
        )

        code = protocol_base.IRCode(
            self,
            packet[:] + packet[:] * (repeat_count + 1),
            [packet[:], packet[:]] * (repeat_count + 1),
            params,
            repeat_count
        )

        return code
