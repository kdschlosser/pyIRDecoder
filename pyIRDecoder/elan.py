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


TIMING = 398


class Elan(protocol_base.IrProtocolBase):
    """
    IR decoder for the 48NEC protocol.
    """
    irp = '{0k,398,msb}<1,-1|1,-2>(3,-2,D:8,~D:8,2,-2,F:8,~F:8,1,^50m)*'
    frequency = 0
    bit_count = 32
    encoding = 'msb'

    _lead_in = [TIMING * 3, -TIMING * 2]
    _lead_out = [TIMING, 50000]
    _middle_timings = [(TIMING * 2, -TIMING * 2)]
    _bursts = [[TIMING, -TIMING], [TIMING, -TIMING * 2]]

    _code_order = [
        ['D', 8],
        ['F', 8]
    ]

    _parameters = [
        ['D', 0, 7],
        ['D_CHECKSUM', 8, 15],
        ['F', 16, 23],
        ['F_CHECKSUM', 24, 31]
    ]
    # [D:0..255,F:0..255]
    encode_parameters = [
        ['device', 0, 255],
        ['function', 0, 255],
    ]

    def _calc_checksum(self, device, function):
        d = self._invert_bits(device, 8)
        f = self._invert_bits(function, 8)
        return d, f

    def decode(self, data, frequency=0):
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)
        if self._last_code is not None:
            if self._last_code == code:
                return self._last_code

            self._last_code.repeat_timer.stop()

            self._last_code = None

        dev_checksum, func_checksum = self._calc_checksum(code.device, code.function)

        if dev_checksum != code.d_checksum or func_checksum != code.f_checksum:
            raise DecodeError('Checksum failed')

        self._last_code = code

        return code

    def encode(self, device, function, repeat_count=0):
        dev_checksum, func_checksum = self._calc_checksum(
            device,
            function
        )
        packet = self._build_packet(
            list(self._get_timing(device, i) for i in range(8)),
            list(self._get_timing(dev_checksum, i) for i in range(8)),
            self._middle_timings[0],
            list(self._get_timing(function, i) for i in range(8)),
            list(self._get_timing(func_checksum, i) for i in range(8)),
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
            1194, -796, 398, -398, 398, -796, 398, -796, 398, -796, 398, -398, 398, -796, 398, -398, 398, -796,
            398, -796, 398, -398, 398, -398, 398, -398, 398, -796, 398, -398, 398, -796, 398, -398, 796, -796,
            398, -398, 398, -796, 398, -796, 398, -398, 398, -796, 398, -796,  398, -796, 398, -398, 398, -796,
            398, -398, 398, -398, 398, -796, 398, -398, 398, -398, 398, -398, 398, -796, 398, -14180
        ]]

        params = [dict(device=117, function=110)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(device=117, function=110)
        protocol_base.IrProtocolBase._test_encode(self, params)


Elan = Elan()
