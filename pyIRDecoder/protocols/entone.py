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


TIMING = 444


class Entone(protocol_base.IrProtocolBase):
    """
    IR decoder for the Entone protocol.
    """
    irp = (
        '{36k,444,msb}<-1,1|1,-1>'
        '(6,-2,1:1,M:3,<-2,2|2,-2>(T:1),0xE60396FFFFF:44,F:8,0:4,-131.0m)*'
        '{M=6,T=0}'
    )
    frequency = 36000
    bit_count = 61
    encoding = 'msb'

    _lead_in = [TIMING * 6, -TIMING * 2]
    _lead_out = [-131000]
    _middle_timings = [{
        'start': 4,
        'stop': 5,
        'bursts': [[-TIMING * 2, TIMING * 2], [TIMING * 2, -TIMING * 2]]
    }]
    _bursts = [[-TIMING, TIMING], [TIMING, -TIMING]]

    _repeat_lead_in = [TIMING * 16, -TIMING * 8]
    _repeat_lead_out = [TIMING, 108000]
    _repeat_bursts = []

    _code_order = [
        ['F', 8]
    ]

    _parameters = [
        ['C0', 0, 0],
        ['M', 1, 3],
        ['T', 4, 4],
        ['C1', 5, 48],
        ['F', 49, 56],
        ['C2', 57, 60]
    ]
    # [F:0..255]
    encode_parameters = [
        ['function', 0, 255]
    ]

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)
        if self._last_code is not None:
            if self._last_code == code:
                return self._last_code

            self._last_code.repeat_timer.stop()
            self._last_code = None

        if (
            code.c0 != 1 or
            code.mode != 6 or
            code.c1 != 0xE60396FFFFF or
            code.c2 != 0
        ):
            raise DecodeError('Checksum failed')

        self._last_code = code
        return code

    def encode(self, function, repeat_count=0):
        function = protocol_base.IntegerWrapper(
            function,
            8,
            self._bursts,
            self.encoding
        )

        c0 = protocol_base.IntegerWrapper(
            1,
            1,
            self._bursts,
            self.encoding
        )

        c1 = protocol_base.IntegerWrapper(
            0xE60396FFFFF,
            44,
            self._bursts,
            self.encoding
        )

        c2 = protocol_base.IntegerWrapper(
            0,
            4,
            self._bursts,
            self.encoding
        )

        mode = protocol_base.IntegerWrapper(
            6,
            3,
            self._bursts,
            self.encoding
        )

        toggle = self._middle_timings[0]['bursts'][0]

        packet = self._build_packet(
            c0.timings,
            mode.timings,
            toggle,
            c1.timings,
            function.timings,
            c2.timings,
        )

        params = dict(
            frequency=self.frequency,
            F=function,
        )

        code = protocol_base.IRCode(
            self,
            packet[:] * (repeat_count + 1),
            [packet[:]] * (repeat_count + 1),
            params,
            repeat_count
        )
        return code
