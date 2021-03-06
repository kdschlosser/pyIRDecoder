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
from . import rcaold

TIMING = 460


class RCA38Old(rcaold.RCAOld.__class__):
    """
    IR decoder for the RCA38Old protocol.
    """
    irp = '{38.7k,460,msb}<1,-2|1,-4>([40][8],-8,D:4,F:8,~D:4,~F:8,2,-16)'
    frequency = 38700
  
    def _test_decode(self):
        rlc = [
            [
                18400, -3680, 460, -920, 460, -1840, 460, -920, 460, -1840, 460, -920, 460, -920, 460, -1840,
                460, -920, 460, -920, 460, -920, 460, -920, 460, -1840, 460, -1840, 460, -920, 460, -1840,
                460, -920, 460, -1840, 460, -1840, 460, -920, 460, -1840, 460, -1840, 460, -1840, 460, -1840,
                460, -920, 920, -7360
            ],
            [
                3680, -3680, 460, -920, 460, -1840, 460, -920, 460, -1840, 460, -920, 460, -920, 460, -1840,
                460, -920, 460, -920, 460, -920, 460, -920, 460, -1840, 460, -1840, 460, -920, 460, -1840,
                460, -920, 460, -1840, 460, -1840, 460, -920, 460, -1840, 460, -1840, 460, -1840, 460, -1840,
                460, -920, 920, -7360
            ]
        ]

        params = [dict(device=5, function=33), None]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(device=5, function=33)
        protocol_base.IrProtocolBase._test_encode(self, params)


RCA38Old = RCA38Old()
