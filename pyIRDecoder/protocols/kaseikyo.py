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

from typing import Sequence

# Local imports
from . import protocol_base
from . import DecodeError


TIMING = 432


class Kaseikyo(protocol_base.IrProtocolBase):
    """
    IR decoder for the Kaseikyo protocol.
    """
    irp = (
        '{37k,432,lsb}<1,-1|1,-3>'
        '(8,-4,M:8,N:8,X:4,D:4,S:8,F:8,E:4,C:4,1,-173)*'
        '{X=((M^N)::4)^(M^N),chksum=D^S^F^(E*16),C=chksum::4^chksum}'
    )
    frequency = 37000
    bit_count = 48
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
        ['F', 8],
        ['E', 4]
    ]

    _parameters = [
        ['OEM1', 0, 7],
        ['OEM2', 8, 15],
        ['X', 16, 19],
        ['D', 20, 23],
        ['S', 24, 31],
        ['F', 32, 39],
        ['E', 40, 43],
        ['CHECKSUM', 44, 47]
    ]
    # [D:0..15,S:0..255,F:0..255,E:0..15,M:0..255,N:0..255]
    encode_parameters = [
        ['device', 0, 15],
        ['sub_device', 0, 255],
        ['function', 0, 255],
        ['extended_function', 0, 15],
        ['oem1', 0, 255],
        ['oem2', 0, 255]
    ]

    @staticmethod
    def _calc_checksum(
        oem1: protocol_base.IntegerWrapper,
        oem2: protocol_base.IntegerWrapper,
        device: protocol_base.IntegerWrapper,
        sub_device: protocol_base.IntegerWrapper,
        function: protocol_base.IntegerWrapper,
        extended_function: protocol_base.IntegerWrapper
    ) -> Sequence[protocol_base.IntegerWrapper]:
        x = ((oem1 ^ oem2) >> 4) ^ (oem1 ^ oem2)
        checksum = device ^ sub_device ^ function ^ (extended_function * 16)
        checksum = checksum >> 4 ^ checksum

        return x[:4:0], checksum[:4:0]

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)

        if self._last_code is not None:
            if self._last_code == code:
                return self._last_code

            self._last_code.repeat_timer.stop()
            self._last_code = None

        if code.oem1 == 3 and code.oem2 == 1:
            raise DecodeError('JVC48 protocol')
        if code.oem1 == 35 and code.oem2 == 203:
            raise DecodeError('MitsubishiK protocol')
        if code.oem1 == 2 and code.oem2 == 32:
            raise DecodeError('Panasonic protocol')
        if code.oem1 == 170 and code.oem2 == 90:
            raise DecodeError('SharpDVD protocol')
        if code.oem1 == 67 and code.oem2 == 83:
            raise DecodeError('TeacK protocol')
        if code.oem1 == 84 and code.oem2 == 50:
            raise DecodeError('DenonK protocol')
        if code.oem1 == 20 and code.oem2 == 99:
            raise DecodeError('Fijitsu protocol')

        x, checksum = self._calc_checksum(
            code.oem1,
            code.oem2,
            code.device,
            code.sub_device,
            code.function,
            code.extended_function
        )

        if x != code.x or checksum != code.checksum:
            raise DecodeError('Checksum failed')

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
        repeat_count: int = 0
    ) -> protocol_base.IRCode:

        if oem1 == 3 and oem2 == 1:
            from . import JVC48
            return JVC48.encode(
                device,
                sub_device,
                function,
                repeat_count
            )
        if oem1 == 35 and oem2 == 203:
            from . import MitsubishiK
            return MitsubishiK.encode(
                device,
                sub_device,
                function,
                repeat_count
            )
        if oem1 == 2 and oem2 == 32:
            from . import Panasonic
            return Panasonic.encode(
                device,
                sub_device,
                function,
                repeat_count
            )
        if oem1 == 170 and oem2 == 90:
            from . import SharpDVD
            return SharpDVD.encode(
                device,
                sub_device,
                function,
                extended_function,
                repeat_count
            )
        if oem1 == 67 and oem2 == 83:
            from . import TeacK
            return TeacK.encode(
                device,
                sub_device,
                function,
                extended_function,
                repeat_count
            )
        if oem1 == 84 and oem2 == 50:
            from . import DenonK
            return DenonK.encode(
                device,
                sub_device,
                function,
                repeat_count
            )
        if oem1 == 20 and oem2 == 99:
            from . import Fujitsu
            return Fujitsu.encode(
                device,
                sub_device,
                function,
                extended_function,
                repeat_count
            )

        device = protocol_base.IntegerWrapper(
            device,
            4,
            cls._bursts,
            cls.encoding
        )
        sub_device = protocol_base.IntegerWrapper(
            sub_device,
            8,
            cls._bursts,
            cls.encoding
        )
        function = protocol_base.IntegerWrapper(
            function,
            8,
            cls._bursts,
            cls.encoding
        )
        extended_function = protocol_base.IntegerWrapper(
            extended_function,
            4,
            cls._bursts,
            cls.encoding
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

        x, checksum = cls._calc_checksum(
            oem1,
            oem2,
            device,
            sub_device,
            function,
            extended_function
        )

        params = dict(
            OEM1=oem1,
            OEM2=oem2,
            D=device,
            S=sub_device,
            F=function,
            E=extended_function,
            X=x,
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
