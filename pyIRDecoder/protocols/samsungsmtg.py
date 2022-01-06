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


TIMING = 497


class SamsungSMTG(protocol_base.IrProtocolBase):
    """
    IR decoder for the SamsungSMTG protocol.
    """
    irp = (
        '{38.5k,497,msb}<1,-1|1,-3>'
        '(4497u,-4497u,D:16,1,-4497u,S:4,F:16,1,^120m)*'
    )
    frequency = 38500
    bit_count = 36
    encoding = 'msb'

    _lead_in = [4497, -4497]
    _lead_out = [TIMING, 120000]
    _middle_timings = [(TIMING, -4497)]
    _bursts = [[TIMING, -TIMING], [TIMING, -TIMING * 3]]

    _code_order = [
        ['D', 16],
        ['S', 4],
        ['F', 16],
    ]

    _parameters = [
        ['D', 0, 15],
        ['S', 16, 19],
        ['F', 20, 35]
    ]
    # [D:0..65335,S:0..15,F:0..65535]
    encode_parameters = [
        ['device', 0, 65335],
        ['sub_device', 0, 15],
        ['function', 0, 65335],
    ]

    def encode(
        self,
        device: int,
        sub_device: int,
        function: int,
        repeat_count: int = 0
    ) -> protocol_base.IRCode:
        device = protocol_base.IntegerWrapper(
            device,
            16,
            self._bursts,
            self.encoding
        )
        sub_device = protocol_base.IntegerWrapper(
            sub_device,
            4,
            self._bursts,
            self.encoding
        )
        function = protocol_base.IntegerWrapper(
            function,
            16,
            self._bursts,
            self.encoding
        )

        packet = self._build_packet(
            device.timings,
            self._middle_timings,
            sub_device.timings,
            function.timings
        )

        params = dict(
            frequency=self.frequency,
            D=device,
            S=sub_device,
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
