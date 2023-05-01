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
# *****************************************************************************

from pyIRDecoder import (
    RepeatLeadInError, 
    RepeatLeadOutError,
    IRException
)
from pyIRDecoder import protocols

protocol = protocols.F12


class F12(object):
    rlc = [[
        1266, -422, 422, -1266, 1266, -422, 1266, -422, 422, -1266, 422, -1266,
        1266, -422, 422, -1266, 422, -1266, 1266, -422, 1266, -422, 1266,
        -34182
    ], [
        1266, -422, 422, -1266, 1266, -422, 1266, -422, 422, -1266, 422, -1266,
        1266, -422, 422, -1266, 422, -1266, 1266, -422, 1266, -422, 1266,
        -34182
    ]]

    params = [
        None,
        dict(device=5, function=228, sub_device=1)
    ]


def test_decode():
    for rlc, params in zip(F12.rlc, F12.params):
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
        print(ir_code)


def test_encode():
    for params in F12.params:
        if params is None:
            continue

        ir_code = protocol.encode(**params)
        for key, value in params.items():
            assert getattr(ir_code, key) == value, (
                key,
                getattr(ir_code, key),
                value
            )

        new_ir_code = None
        for rlc in ir_code.normalized_rlc:
            try:
                new_ir_code = protocol.decode(rlc, protocol.frequency)
            except (RepeatLeadInError, RepeatLeadOutError):
                continue
            except IRException:
                new_ir_code = protocol.decode(
                    ir_code.original_rlc,
                    protocol.frequency
                )
                break

        print()
        print(ir_code)
        print(new_ir_code)
        
        assert new_ir_code == ir_code

        break