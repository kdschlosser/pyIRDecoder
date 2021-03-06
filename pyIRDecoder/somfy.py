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


class Somfy(protocol_base.IrProtocolBase):
    """
    IR decoder for the Somfy protocol.
    """
    irp = '{35.7k,1,lsb}<308,-881|669,-520>(2072,-484,F:2,D:3,C:4,-2300)*{C=F*4+D+3}'
    frequency = 35700
    bit_count = 9
    encoding = 'lsb'

    _lead_in = [2072, -484]
    _lead_out = [-2300]
    _middle_timings = []
    _bursts = [[308, -881], [669, -520]]

    _code_order = [
        ['F', 2],
        ['D', 3],
    ]

    _parameters = [
        ['F', 0, 1],
        ['D', 2, 4],
        ['CHECKSUM', 5, 8]
    ]
    # [F:0..3,D:0..7]
    encode_parameters = [
        ['device', 0, 7],
        ['function', 0, 3],
    ]

    def _calc_checksum(self, device, function):
        # {C=F*4+D+3}
        return self._get_bits(function * 4 + device + 3, 0, 3)

    def decode(self, data, frequency=0):
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)

        if self._last_code is not None:
            if self._last_code == code:
                return self._last_code

            self._last_code.refresh_timer.stop()
            self._last_code = None

        checksum = self._calc_checksum(code.device, code.function)

        if checksum != code.checksum:
            raise DecodeError('Checksum failed')

        self._last_code = code
        return code

    def encode(self, device, function, repeat_count=0):
        checksum = self._calc_checksum(device, function)

        packet = self._build_packet(
            list(self._get_timing(function, i) for i in range(2)),
            list(self._get_timing(device, i) for i in range(3)),
            list(self._get_timing(checksum, i) for i in range(4)),
        )

        params = dict(
            frequency=self.frequency,
            D=device,
            F=function,
        )

        code = protocol_base.IRCode(
            self,
            [packet[:]],
            [packet[:]] * (repeat_count + 1),
            params,
            repeat_count
        )

        return code

    def _test_decode(self):
        rlc = [[
            2072, -484, 669, -520, 669, -520, 308, -881, 669, -520, 308, -881, 669, -520, 
            308, -881, 308, -881, 308, -3181, 
        ]]

        params = [dict(device=2, function=3)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(device=2, function=3)
        protocol_base.IrProtocolBase._test_encode(self, params)


Somfy = Somfy()

