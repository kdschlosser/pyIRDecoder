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
from . import arctech
from . import protocol_base


class Arctech38(arctech.Arctech.__class__):
    """
    IR decoder for the Arctech38 protocol.
    """
    irp = '{38k,388,lsb}<1,-3|3,-1>(<0:2|2:2>((D-1):4,(S-1):4),40:7,F:1,0:1,-10.2m)*'
    frequency = 38000

    def _test_decode(self):
        rlc = [[
            388, -1164, 388, -1164, 388, -1164, 1164, -388, 388, -1164, 1164, -388, 388, -1164,
            1164, -388, 388, -1164, 1164, -388, 388, -1164, 388, -1164, 388, -1164, 1164, -388,
            388, -1164, 388, -1164, 388, -1164, 388, -1164, 388, -1164, 1164, -388, 388, -1164,
            1164, -388, 388, -1164, 1164, -388, 388, -11364,
        ]]

        params = [dict(device=15, function=1, sub_device=6)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(device=15, function=1, sub_device=6)
        protocol_base.IrProtocolBase._test_encode(self, params)




Arctech38 = Arctech38()
