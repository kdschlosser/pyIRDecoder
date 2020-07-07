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
from . import DecodeError

from . import denon

TIMING = 264


class Denon1(denon.Denon.__class__):
    """
    IR decoder for the Denon1 protocol.
    """
    irp = '{38k,264,lsb}<1,-3|1,-7>(D:5,F:8,0:2,1,-165)*'

    def encode(self, device, function, repeat_count=0):
        return denon.Denon.encode(device, function, repeat_count)

    def _test_decode(self):
        rlc = [[
            264, -1848, 264, -1848, 264, -1848, 264, -792, 264, -792, 264, -1848, 264, -792, 264, -792, 264, -792,
            264, -792, 264, -1848, 264, -792, 264, -1848, 264, -792, 264, -792, 264, -43560
        ]]

        params = [dict(device=7, function=161)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(device=7, function=161)
        protocol_base.IrProtocolBase._test_encode(self, params)


Denon1 = Denon1()
