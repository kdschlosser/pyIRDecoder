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
from . import amino
from . import protocol_base


class Amino56(amino.Amino.__class__):
    """
    IR decoder for the Amino56 protocol.
    """
    irp = (
        '{56.0k,268,msb}<-1,1|1,-1>([T=1][T=0],7,-6,3,D:4,1:1,T:1,1:2,0:8,F:8,15:4,C:4,-79m)+'
        '{C=(D:4+4*T+9+F:4+F:4:4+15)&15}'
    )
    frequency = 56000

    def _test_decode(self):
        rlc = [[
            1876, -1608, 804, -268, 536, -268, 268, -268, 268, -268, 268, -268, 268, -536, 536, -536, 268, -268,
            268, -268, 268, -268, 268, -268, 268, -268, 268, -268, 268, -268, 536, -268, 268, -268, 268, -268,
            268, -268, 268, -536, 268, -268, 536, -268, 268, -268, 268, -268, 268, -268, 268, -268, 268, -536,
            536, -268, 268, -79268
        ]]

        params = [dict(device=7, function=249)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(device=7, function=249)
        protocol_base.IrProtocolBase._test_encode(self, params)


Amino56 = Amino56()
