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


TIMING = 400


class SharpDVD(protocol_base.IrProtocolBase):
    """
    IR decoder for the SharpDVD protocol.
    """
    irp = (
        '{38k,400,lsb}<1,-1|1,-3>'
        '(8,-4,170:8,90:8,15:4,D:4,S:8,F:8,E:4,C:4,1,-48)*'
        '{C=D^S:4:0^S:4:4^F:4:0^F:4:4^E:4}'
    )
    frequency = 38000
    bit_count = 48
    encoding = 'lsb'

    _lead_in = [TIMING * 8, -TIMING * 4]
    _lead_out = [TIMING, -TIMING * 48]
    _middle_timings = []
    _bursts = [[TIMING, -TIMING], [TIMING, -TIMING * 3]]

    _code_order = [
        ['D', 4],
        ['S', 8],
        ['F', 8],
        ['E', 4]
    ]

    _parameters = [
        ['C0', 0, 7],
        ['C1', 8, 15],
        ['C2', 16, 19],
        ['D', 20, 23],
        ['S', 24, 31],
        ['F', 32, 39],
        ['E', 40, 43],
        ['CHECKSUM', 44, 47]
    ]
    # [D:0..15,S:0..255,F:0..255,E:0..15=1]
    encode_parameters = [
        ['device', 0, 15],
        ['sub_device', 0, 255],
        ['function', 0, 255],
        ['extended_function', 0, 15]
    ]

    @staticmethod
    def _calc_checksum(
        device: protocol_base.IntegerWrapper,
        sub_device: protocol_base.IntegerWrapper,
        function: protocol_base.IntegerWrapper,
        extended_function: protocol_base.IntegerWrapper
    ) -> protocol_base.IntegerWrapper:
        f1 = function[:4:0]
        f2 = function[:4:4]
        s1 = sub_device[:4:0]
        s2 = sub_device[:4:4]
        e = extended_function[:4:0]

        return (device ^ s1 ^ s2 ^ f1 ^ f2 ^ e)[:4:0]

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)

        checksum = self._calc_checksum(
            code.device,
            code.sub_device,
            code.function,
            code.extended_function
        )

        if (
            code.c0 != 170 or
            code.c1 != 90 or
            code.c2 != 15 or
            checksum != code.checksum
        ):
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
        device: int,
        sub_device: int,
        function: int,
        extended_function: int,
        repeat_count: int = 0
    ) -> protocol_base.IRCode:

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

        checksum = cls._calc_checksum(
            device,
            sub_device,
            function,
            extended_function
        )

        params = dict(
            C0=170,
            C1=90,
            C2=15,
            D=device,
            S=sub_device,
            F=function,
            E=extended_function,
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
