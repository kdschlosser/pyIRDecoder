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
from . import DecodeError, RepeatLeadOut

TIMING = 264


class Denon(protocol_base.IrProtocolBase):
    """
    IR decoder for the Denon protocol.
    """
    irp = '{38k,264,lsb}<1,-3|1,-7>(D:5,F:8,0:2,1,-165,D:5,~F:8,3:2,1,-165)*'
    frequency = 38000
    bit_count = 15
    encoding = 'lsb'

    _lead_in = []
    _lead_out = [TIMING, -TIMING * 165]
    _middle_timings = []
    _bursts = [[TIMING, -TIMING * 3], [TIMING, -TIMING * 7]]

    _repeat_lead_in = []
    _repeat_lead_out = []
    _repeat_bursts = []

    _parameters = [
        ['D', 0, 4],
        ['F', 5, 12],
        ['CHECKSUM', 13, 14]
    ]
    # [D:0..31,F:0..255]
    encode_parameters = [
        ['device', 0, 31],
        ['function', 0, 255],
    ]

    def _calc_checksum(self, function):
        f = self._invert_bits(function, 8)
        return f

    def decode(self, data, frequency=0):
        try:
            code = protocol_base.IrProtocolBase.decode(self, data, frequency)
        except DecodeError as err:
            self._last_code = None
            raise err

        if code.checksum == 0:
            self._last_code = code
            return code

        if code.checksum == 3:
            if self._last_code is None:
                function = self._calc_checksum(code.function)

                params = dict(
                    D=code.device,
                    F=function,
                    frequency=self.frequency
                )
                from . import denon2
                return protocol_base.IRCode(denon2.Denon2, code.original_rlc, code.normalized_rlc, params)

            if code.device == self._last_code.device:
                func_checksum = self._calc_checksum(self._last_code.function)

                if func_checksum != code.function:
                    self._last_code = None
                    raise DecodeError('Checksum failed')

                self._last_code = None
                raise RepeatLeadOut

        else:
            self._last_code = None
            raise DecodeError('Invalid checksum')

    def encode(self, device, function):
        c0 = 0
        c1 = 3
        func_checksum = self._calc_checksum(function)

        packet1 = self._build_packet(
            list(self._get_timing(device, i) for i in range(5)),
            list(self._get_timing(function, i) for i in range(8)),
            list(self._get_timing(c0, i) for i in range(2))
        )
        packet2 = self._build_packet(
            list(self._get_timing(device, i) for i in range(5)),
            list(self._get_timing(func_checksum, i) for i in range(8)),
            list(self._get_timing(c1, i) for i in range(2)),
        )

        return [packet1, packet2]

    def _test_decode(self):
        rlc = [
            [
                +264, -1848, +264, -792, +264, -1848, +264, -1848, +264, -1848, +264, -1848, +264, -1848, +264, -1848,
                +264, -792, +264, -792, +264, -1848, +264, -1848, +264, -1848, +264, -792, +264, -792, +264, -43560
            ],
            [
                +264, -1848, +264, -792, +264, -1848, +264, -1848, +264, -1848, +264, -792, +264, -792, +264, -792,
                +264, -1848, +264, -1848, +264, -792, +264, -792, +264, -792, +264, -1848, +264, -1848, +264, -43560
            ]
        ]

        params = [dict(device=26, function=238)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(device=26, function=238)
        protocol_base.IrProtocolBase._test_encode(self, params)


Denon = Denon()

