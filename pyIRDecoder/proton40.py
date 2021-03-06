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
from . import proton
from . import protocol_base


TIMING = 500


class Proton40(proton.Proton.__class__):
    """
    IR decoder for the Proton40 protocol.
    """
    irp = '{40.5k,500,lsb}<1,-1|1,-3>(16,-8,D:8,1,-8,F:8,1,^63m)*'
    frequency = 40500

    def _test_decode(self):
        rlc = [[
            8000, -4000, 500, -500, 500, -500, 500, -1500, 500, -1500, 500, -1500, 500, -500,
            500, -1500, 500, -1500, 500, -4000, 500, -1500, 500, -500, 500, -500, 500, -1500,
            500, -1500, 500, -500, 500, -500, 500, -1500, 500, -21000,
        ]]

        params = [dict(device=220, function=153)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(device=220, function=153)
        protocol_base.IrProtocolBase._test_encode(self, params)


Proton40 = Proton40()
