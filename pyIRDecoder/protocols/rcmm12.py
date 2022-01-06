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
from . import DecodeError

TIMING = 28.777777777777


# noinspection PyAbstractClass
class RCMM12(protocol_base.IrProtocolBase):
    irp = '{36k,1p,msb}<6, -10|6,-16|6,-22|6,-28>(15,-10,M:2,A:2,F:8)*'
    frequency = 36000
    bit_count = 12
    encoding = 'msb'

    _lead_in = [int(TIMING * 15), int(-TIMING * 10)]
    _bursts = [
        [int(TIMING * 6), int(-TIMING * 10)],
        [int(TIMING * 6), int(-TIMING * 16)],
        [int(TIMING * 6), int(-TIMING * 22)],
        [int(TIMING * 6), int(-TIMING * 28)]
    ]

    _code_order = [
        ['M', 2],
        ['A', 2],
        ['F', 8]
    ]

    _parameters = [
        ['M', 0, 1],
        ['A', 2, 3],
        ['F', 4, 11]
    ]
    # [D:0..15,F:0..255]
    encode_parameters = [
        ['mode', 0, 3],
        ['address', 0, 3],
        ['function', 0, 255]
    ]

    MODE_MAPPING = {
        0: 'Extended',
        1: 'Mouse',
        2: 'Keyboard',
        3: 'Gamepad'
    }

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        # in this protocol each burst pair represents 2 bits
        # so a 12 bit code is going to have 6 burst pairs and
        # a 24 bit code will have 12 burst pairs
        # excluding the header and footer

        code = protocol_base.IrProtocolBase.decode(self, data, frequency)

        if code.mode == 0:
            raise DecodeError('Extended protocol')

        if self._last_code is not None:
            if self._last_code == code:
                return self._last_code

            self._last_code.repeat_timer.stop()

        self._last_code = code
        return code

    def encode(
        self,
        mode: int,
        address: int,
        function: int,
        repeat_count: int = 0
    ) -> protocol_base.IRCode:

        params = dict(
            M=mode,
            A=address,
            F=function
        )

        packet = self._build_packet(**params)
        params['frequency'] = self.frequency

        code = protocol_base.IRCode(
            self,
            packet[:] * (repeat_count + 1),
            [packet[:]] * (repeat_count + 1),
            params
        )
        return code
