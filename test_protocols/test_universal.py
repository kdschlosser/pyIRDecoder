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

from pyIRDecoder import (
    RepeatLeadInError, 
    RepeatLeadOutError,
    IRException
)
from pyIRDecoder import protocols

protocol = protocols.Universal


class Universal(object):
    rlc = [[
        25000, -500, 500, -1000, 500, -500, 1000, -500, 500, -1000, 500, -500,
        1000, -1000, 500, -500, 1000, -500, 500, -1000, 1000, -500, 500, -1000,
        1000, -500, 500, -500, 500, -1000, 500, -500, 1000, -1000, 1000, -500,
        500, -1000, 1000, -1000, 1000, -500, 500, -500, 500, -1000, 1000,
        -1000, 1000, -500, 500, -500, 500, -500, 500, -1000, 1000, -1000, 1000,
        -500, 500, -500, 500, -1000, 1000, -1000, 1000, -1000, 500, -500, 500,
        -500, 500, -500, 1000, -500, 500, -500, 500, -500, 500, -1000, 500,
        -500, 1000, -500, 500, -1000, 1000, -500, 500, -500, 500, -25500
    ]]
    params = [dict(code=0x1E6C91A51428AF0C8)]


def test_decode():
    for rlc, params in zip(Universal.rlc, Universal.params):
        try:
            ir_code = protocol.decode(rlc, protocol.frequency)
        except (RepeatLeadInError, RepeatLeadOutError):
            if params is not None:
                raise
            continue
        
        for key, value in params.items():
            assert getattr(ir_code, key) == value, (
                key,
                getattr(ir_code, key),
                value
            )
        print()
        print(ir_code, repr(ir_code))
