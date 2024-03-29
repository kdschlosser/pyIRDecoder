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


TIMING = 388

BIT_MAPPING = {
    0: 1,
    2: 2,
    8: 3,
    10: 4,
    32: 5,
    34: 6,
    40: 7,
    42: 8,
    128: 9,
    130: 10,
    136: 11,
    138: 12,
    160: 13,
    162: 14,
    168: 15,
    170: 16,
}


class Arctech(protocol_base.IrProtocolBase):
    """
    IR decoder for the Arctech protocol.
    """
    irp = (
        '{0k,388,lsb}<1,-3|3,-1>(<0,2|2,2>((D-1):4,(S-1):4),'
        '40:7,F:1,0:1,-10.2m)*'
    )
    frequency = 0
    bit_count = 25
    encoding = 'lsb'

    _lead_in = [TIMING * 16, -TIMING * 8]
    _lead_out = [-10200]
    _bursts = [[TIMING, -TIMING * 3], [TIMING * 3, -TIMING]]

    _code_order = [
        ['D', 4],
        ['S', 4],
        ['F', 1]
    ]

    _parameters = [
        ['D', 0, 7],
        ['S', 8, 15],
        ['C0', 16, 22],
        ['F', 23, 23],
        ['C1', 24, 24],
    ]
    # [D:1..16,S:1..16,F:0..1]
    encode_parameters = [
        ['device', 1, 16],
        ['sub_device', 1, 16],
        ['function', 0, 1],
    ]

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)

        if code.c0 != 40 or code.c1 != 0:
            raise DecodeError('Checksum failed')

        device = BIT_MAPPING[code.device]
        sub_device = BIT_MAPPING[code.sub_device]

        params = {
            'D': device,
            'S': sub_device,
            'C0': code.c0,
            'F': code.function,
            'C1': code.c1,
            'frequency': self.frequency
        }

        code = protocol_base.IRCode(
            self,
            code.original_rlc,
            code.normalized_rlc,
            params
        )

        if self._last_code is not None:
            if self._last_code == code:
                return self._last_code

            self._last_code.repeat_timer.stop()

        self._last_code = code

        return code

    def encode(
        self,
        device: int,
        sub_device: int,
        function: int,
        repeat_count: int = 0
    ) -> protocol_base.IRCode:

        bit_mapping = {v: k for k, v in BIT_MAPPING.items()}

        dev = bit_mapping[device]
        sub_dev = bit_mapping[sub_device]
        params = dict(
            D=dev,
            S=sub_dev,
            C0=40,
            F=function,
            C1=0
        )

        packet = self._build_packet(**params)

        params['frequency'] = self.frequency
        params['D'] = device
        params['S'] = sub_device

        code = protocol_base.IRCode(
            self,
            packet[:] * (repeat_count + 1),
            [packet[:]] * (repeat_count + 1),
            params,
            repeat_count
        )
        return code
