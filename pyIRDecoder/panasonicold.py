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


TIMING = 833


class PanasonicOld(protocol_base.IrProtocolBase):
    """
    IR decoder for the PanasonicOld protocol.
    """
    irp = '{57.6k,833,lsb}<1,-1|1,-3>(4,-4,D:5,F:6,~D:5,~F:6,1,-44m)*'
    frequency = 57600
    bit_count = 22
    encoding = 'lsb'

    _lead_in = [TIMING * 4, -TIMING * 4]
    _lead_out = [TIMING, -44000]
    _middle_timings = []
    _bursts = [[TIMING, -TIMING], [TIMING, -TIMING * 3]]

    _code_order = [
        ['D', 5],
        ['F', 6],
    ]

    _parameters = [
        ['D', 0, 4],
        ['F', 5, 10],
        ['D_CHECKSUM', 11, 15],
        ['F_CHECKSUM', 16, 21],
    ]
    # [D:0..31,F:0..63]
    encode_parameters = [
        ['device', 0, 31],
        ['function', 0, 63],
    ]

    def _calc_checksum(self, device, function):
        f = self._invert_bits(function, 6)
        d = self._invert_bits(device, 5)
        return d, f

    def decode(self, data, frequency=0):
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)
        if self._last_code is not None:
            if self._last_code == code:
                return self._last_code

            self._last_code.repeat_timer.stop()
            self._last_code = None

        dev_checksum, func_checksum = self._calc_checksum(code.device, code.function)

        if func_checksum != code.f_checksum or dev_checksum != code.d_checksum:
            raise DecodeError('Checksum failed')

        self._last_code = code
        return code

    def encode(self, device, function, repeat_count=0):
        dev_checksum, func_checksum = self._calc_checksum(
            device,
            function,
        )

        packet = self._build_packet(
            list(self._get_timing(device, i) for i in range(5)),
            list(self._get_timing(function, i) for i in range(6)),
            list(self._get_timing(dev_checksum, i) for i in range(5)),
            list(self._get_timing(func_checksum, i) for i in range(6))
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
            3332, -3332, 833, -833, 833, -2499, 833, -833, 833, -833, 833, -2499, 833, -833, 
            833, -2499, 833, -833, 833, -2499, 833, -2499, 833, -833, 833, -2499, 833, -833, 
            833, -2499, 833, -2499, 833, -833, 833, -2499, 833, -833, 833, -2499, 833, -833, 
            833, -833, 833, -2499, 833, -44000, 
        ]]

        params = [dict(device=18, function=26)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(device=18, function=26)
        protocol_base.IrProtocolBase._test_encode(self, params)


PanasonicOld = PanasonicOld()
