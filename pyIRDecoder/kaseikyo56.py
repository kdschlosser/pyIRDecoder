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

TIMING = 432


class Kaseikyo56(protocol_base.IrProtocolBase):
    """
    IR decoder for the Kaseikyo56 protocol.
    """
    irp = (
        '{37k,432,lsb}<1,-1|1,-3>(8,-4,M:8,N:8,H:4,D:4,S:8,E:8,F:8,G:8,1,-173)*'
        '{H=((M^N)::4)^(M^N)'
    )
    frequency = 37000
    bit_count = 56
    encoding = 'lsb'

    _lead_in = [TIMING * 8, -TIMING * 4]
    _lead_out = [TIMING, -TIMING * 173]
    _middle_timings = []
    _bursts = [[TIMING, -TIMING], [TIMING, -TIMING * 3]]

    _code_order = [
        ['OEM1', 8],
        ['OEM2', 8],
        ['D', 4],
        ['S', 8],
        ['E', 8],
        ['F', 8],
        ['G', 8]
    ]

    _parameters = [
        ['OEM1', 0, 7],
        ['OEM2', 8, 15],
        ['CHECKSUM', 16, 19],
        ['D', 20, 23],
        ['S', 24, 31],
        ['E', 32, 39],
        ['F', 40, 47],
        ['G', 48, 55]
    ]
    # [D:0..15,S:0..255,F:0..255,G:0..255,M:0..255,N:0..255,E:0..255]
    encode_parameters = [
        ['device', 0, 15],
        ['sub_device', 0, 255],
        ['function', 0, 255],
        ['g', 0, 255],
        ['extended_function', 0, 15],
        ['oem1', 0, 255],
        ['oem2', 0, 255]
    ]

    def _calc_checksum(self, oem1, oem2):
        checksum = ((oem1 ^ oem2) >> 4) ^ (oem1 ^ oem2)
        return self._get_bits(checksum, 0, 3)

    def decode(self, data, frequency=0):
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)
        if self._last_code is not None:
            if self._last_code == code:
                return self._last_code

            self._last_code.repeat_timer.stop()
            self._last_code = None

        if code.oem1 == 3 and code.oem2 == 1:
            raise DecodeError('JVC56 protocol')
        if code.oem1 == 20 and code.oem2 == 99:
            raise DecodeError('Fijitsu56 protocol')

        checksum = self._calc_checksum(
            code.oem1,
            code.oem2
        )

        if checksum != code.checksum:
            raise DecodeError('Checksum failed')

        self._last_code = code
        return code

    def encode(
        self,
        oem1,
        oem2,
        device,
        sub_device,
        function,
        extended_function,
        g,
        repeat_count=0
    ):

        if oem1 == 3 and oem2 == 1:
            from . import jvc56
            return jvc56.JVC56.encod(
                device,
                sub_device,
                function,
                extended_function,
                repeat_count
            )

        if oem1 == 20 and oem2 == 99:
            from . import fujitsu56
            return fujitsu56.Fujitsu56.encode(
                device,
                sub_device,
                function,
                extended_function,
                g,
                repeat_count
            )

        checksum = self._calc_checksum(oem1, oem2)

        packet = self._build_packet(
            list(self._get_timing(oem1, i) for i in range(8)),
            list(self._get_timing(oem2, i) for i in range(8)),
            list(self._get_timing(checksum, i) for i in range(4)),
            list(self._get_timing(device, i) for i in range(4)),
            list(self._get_timing(sub_device, i) for i in range(8)),
            list(self._get_timing(extended_function, i) for i in range(8)),
            list(self._get_timing(function, i) for i in range(8)),
            list(self._get_timing(g, i) for i in range(8))
        )

        params = dict(
            frequency=self.frequency,
            OEM1=oem1,
            OEM2=oem2,
            D=device,
            S=sub_device,
            F=function,
            E=extended_function,
            G=g
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
            3456, -1728, 432, -1296, 432, -1296, 432, -432, 432, -1296, 432, -1296, 432, -1296, 432, -432,
            432, -432, 432, -1296, 432, -432, 432, -1296, 432, -432, 432, -432, 432, -1296, 432, -432,
            432, -1296, 432, -1296, 432, -1296, 432, -1296, 432, -432, 432, -432, 432, -432, 432, -1296,
            432, -432, 432, -432, 432, -1296, 432, -1296, 432, -432, 432, -1296, 432, -432, 432, -1296,
            432, -432, 432, -432, 432, -1296, 432, -1296, 432, -1296, 432, -1296, 432, -1296, 432, -1296,
            432, -432, 432, -1296, 432, -432, 432, -1296, 432, -1296, 432, -432, 432, -1296, 432, -432,
            432, -432, 432, -1296, 432, -1296, 432, -1296, 432, -1296, 432, -432, 432, -1296, 432, -432,
            432, -1296, 432, -74736
        ]]

        params = [dict(device=4, extended_function=126, function=45, g=175, oem1=59, oem2=165, sub_device=86)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(device=4, extended_function=126, function=45, g=175, oem1=59, oem2=165, sub_device=86)
        protocol_base.IrProtocolBase._test_encode(self, params)


Kaseikyo56 = Kaseikyo56()
