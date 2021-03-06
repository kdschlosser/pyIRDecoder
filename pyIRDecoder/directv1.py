# -*- coding: utf-8 -*-
#
# ***********************************************************************************
# MIT License
#
# Copyright (c) 2020 Kevin G. Schlosser
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is furnished
# to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
# CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
# OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# ***********************************************************************************

# Local imports
from . import protocol_base
from . import directv0

TIMING = 600


class DirecTV1(directv0.DirecTV0.__class__):
    """
    IR decoder for the DirecTV1 protocol.
    """
    irp = '{40k,600,msb}<1,-1|1,-2|2,-1|2,-2>([10][5],-2,D:4,F:8,C:4,1,-50){C=7*(F:2:6)+5*(F:2:4)+3*(F:2:2)+(F:2)}'

    _lead_out = [TIMING, -TIMING * 50]

    def _test_decode(self):
        rlc = [
            [
                +6000, -1200, +1200, -1200, +1200, -600, +600, -600, +1200, -600, +1200, -600, +600, -600, +600, -600,
                +600, -600, +600, -30000
            ],
            [
                +3000, -1200, +1200, -1200, +1200, -600, +600, -600, +1200, -600, +1200, -600, +600, -600, +600, -600,
                +600, -600, +600, -30000
            ]
        ]

        params = [
            None,
            dict(device=14, function=40)
        ]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)


DirecTV1 = DirecTV1()
