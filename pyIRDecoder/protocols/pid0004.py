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


TIMING = 1


class PID0004(protocol_base.IrProtocolBase):
    """
    IR decoder for the pid0004 protocol.
    """
    irp = '{0k,1,msb}<12,-130|12,-372>(F:6,12,-27m)*'
    frequency = 0
    bit_count = 6
    encoding = 'msb'

    _lead_in = []
    _lead_out = [12, -27000]
    _middle_timings = []
    _bursts = [[12, -130], [12, -372]]

    _code_order = [
        ['F', 6],
    ]

    _parameters = [
        ['F', 0, 5],
    ]
    # [F:0..63]
    encode_parameters = [
        ['function', 0, 63],
    ]

    def encode(
        self,
        function: int,
        repeat_count: int = 0
    ) -> protocol_base.IRCode:
        params = dict(
            F=function,
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
