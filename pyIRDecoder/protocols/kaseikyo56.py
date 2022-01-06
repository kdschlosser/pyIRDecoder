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

TIMING = 432


class Kaseikyo56(protocol_base.IrProtocolBase):
    """
    IR decoder for the Kaseikyo56 protocol.
    """
    irp = (
        '{37k,432,lsb}<1,-1|1,-3>'
        '(8,-4,M:8,N:8,H:4,D:4,S:8,E:8,F:8,G:8,1,-173)*'
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

    @staticmethod
    def _calc_checksum(
        oem1: protocol_base.IntegerWrapper,
        oem2: protocol_base.IntegerWrapper
    ) -> protocol_base.IntegerWrapper:
        checksum = ((oem1 ^ oem2) >> 4) ^ (oem1 ^ oem2)
        return checksum[:4:0]

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)

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
        if self._last_code is not None:
            if self._last_code == code:
                return self._last_code

            self._last_code.repeat_timer.stop()
            self._last_code = None

        self._last_code = code
        return code

    @classmethod
    def encode(
        cls,
        oem1: int,
        oem2: int,
        device: int,
        sub_device: int,
        function: int,
        extended_function: int,
        g: int,
        repeat_count: int = 0
    ):
        if oem1 == 3 and oem2 == 1:
            from . import JVC56
            return JVC56.encod(
                device,
                sub_device,
                function,
                extended_function,
                repeat_count
            )

        if oem1 == 20 and oem2 == 99:
            from . import Fujitsu56
            return Fujitsu56.encode(
                device,
                sub_device,
                function,
                extended_function,
                g,
                repeat_count
            )

        oem1 = protocol_base.IntegerWrapper(
            oem1,
            8,
            cls._bursts,
            cls.encoding
        )
        oem2 = protocol_base.IntegerWrapper(
            oem2,
            8,
            cls._bursts,
            cls.encoding
        )

        checksum = cls._calc_checksum(oem1, oem2)
        params = dict(
            OEM1=oem1,
            OEM2=oem2,
            D=device,
            S=sub_device,
            F=function,
            E=extended_function,
            G=g,
            CHECKSUM=checksum
        )

        packet = cls._build_packet(**params)

        params['frequency'] = cls.frequency

        code = protocol_base.IRCode(
            cls(),
            packet[:] * (repeat_count + 1),
            [packet[:]] * (repeat_count + 1),
            params,
            repeat_count
        )

        return code
