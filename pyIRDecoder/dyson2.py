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
from . import dyson
from . import protocol_base

TIMING = 780


class Dyson2(dyson.Dyson.__class__):
    """
    IR decoder for the Dyson2 protocol.
    """
    irp = '{38k,780,lsb}<1,-1|1,-2>(3,-1,D:7,F:6,T:-2,1,-400m,3,-1,D:7,F:6,T:-2,1,-60m,(3,-1,1:1,1,-60m)*)'

    _middle_timings = [(TIMING, -400000), (TIMING * 3, -TIMING)]

    def _test_decode(self):
        rlc = [[
            2340, -780, 780, -1560, 780, -780, 780, -780, 780, -1560, 780, -780, 780, -780,
            780, -1560, 780, -780, 780, -1560, 780, -780, 780, -780, 780, -1560, 780, -780,
            780, -780, 780, -780, 780, -400000, 2340, -780, 780, -1560, 780, -780, 780, -780,
            780, -1560, 780, -780, 780, -780, 780, -1560, 780, -780, 780, -1560, 780, -780,
            780, -780, 780, -1560, 780, -780, 780, -780, 780, -780, 780, -60000,
        ]]

        params = [dict(function=18, toggle=0, device=73)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(function=18, toggle=0, device=73)
        protocol_base.IrProtocolBase._test_encode(self, params)


Dyson2 = Dyson2()
