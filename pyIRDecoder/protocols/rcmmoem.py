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
from . import rcmm12

TIMING = 28.777777777777


# noinspection PyAbstractClass, PyProtectedMember
class RCMMOEM(rcmm12.RCMM12):
    irp = '{36k,1p,msb}<6, -10|6,-16|6,-22|6,-28>(15,-10,M:6,ID:6,F:12)*'
    bit_count = 24
    encoding = 'msb'

    _code_order = [
        ['ID', 6],
        ['F', 12]
    ]

    _parameters = [
        ['M', 0, 5],
        ['ID', 6, 11],
        ['F', 12, 23]
    ]
    # [id:0..63,F:0..4095]
    encode_parameters = [
        ['id', 0, 63],
        ['function', 0, 4095]
    ]

    MODE_MAPPING = {
        3: 'OEM'
    }

    # noinspection PyShadowingBuiltins, PyMethodOverriding
    def encode(
        self,
        id: int,
        function: int,
        repeat_count: int = 0
    ) -> protocol_base.IRCode:

        params = dict(
            M=3,
            ID=id,
            F=function
        )

        # noinspection PyUnresolvedReferences
        packet = self._build_packet(**params)
        # noinspection PyUnresolvedReferences
        params['frequency'] = self.frequency

        code = protocol_base.IRCode(
            self,
            packet[:] * (repeat_count + 1),
            [packet[:]] * (repeat_count + 1),
            params
        )
        return code
