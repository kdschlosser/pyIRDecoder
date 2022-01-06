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
from . import DecodeError, RepeatLeadInError


TIMING = 564


class PioneerMix(protocol_base.IrProtocolBase):
    """
    IR decoder for the PioneerMix protocol.
    """
    irp = (
        '{40k,564, lsb}<1,-1|1,-3>'
        '(16,-8,D0:8,~D0:8,F0:8,~F0:8,1,^108m,'
        '(16,-8,D :8,~D :8,F :8,~F :8,1,^108m)+) '
    )
    frequency = 40000
    bit_count = 32
    encoding = 'lsb'

    _lead_in = [TIMING * 16, -TIMING * 8]
    _lead_out = [TIMING, 108000]
    _middle_timings = []
    _bursts = [[TIMING, -TIMING], [TIMING, -TIMING * 3]]

    _code_order = [
        ['D', 8],
        ['F', 8],
    ]

    _parameters = [
        ['D', 0, 7],
        ['D_CHECKSUM', 8, 15],
        ['F', 16, 23],
        ['F_CHECKSUM', 24, 31]
    ]
    # [D0:0..255,F0:0..255,D:0..255=D0,F:0..255=F0]
    encode_parameters = [
        ['device', 0, 255],
        ['function', 0, 255],
    ]

    @staticmethod
    def _calc_checksum(
        device: protocol_base.IntegerWrapper,
        function: protocol_base.IntegerWrapper
    ) -> Sequence[protocol_base.IntegerWrapper]:
        return device[True:8:0], function[True:8:0]

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)

        d_checksum, f_checksum = (
            self._calc_checksum(code.device, code.function)
        )

        if d_checksum != code.d_checksum or f_checksum != code.f_checksum:
            raise DecodeError('Checksum failed')

        if self._last_code is not None:
            if hasattr(self._last_code, 'd0'):
                if (
                    self._last_code.device == code.device and
                    self._last_code.function == code.function
                ):
                    return self._last_code
            else:
                params = dict(
                    frequency=self.frequency,
                    D0=self._last_code.device,
                    D0_CHECKSUM=self._last_code.d_checksum,
                    F0=self._last_code.function,
                    F0_CHECKSUM=self._last_code.f_checksum,
                    D=code.device,
                    D_CHECKSUM=code.d_checksum,
                    F=code.function,
                    F_CHECKSUM=code.f_checksum
                )
                original_rlc = self._last_code.original_rlc
                normalized_rlc = self._last_code.normalized_rlc
                original_rlc += code.original_rlc
                normalized_rlc += code.normalized_rlc

                code = protocol_base.IRCode(
                    self,
                    original_rlc,
                    normalized_rlc,
                    params
                )
                self._last_code = code
                return code

            self._last_code.repeat_timer.stop()
            self._last_code = None

        self._last_code = code
        raise RepeatLeadInError

    def encode(
        self,
        device: int,
        function: int,
        d0: int,
        f0: int,
        repeat_count: int = 0
    ):
        device = protocol_base.IntegerWrapper(
            device,
            8,
            self._bursts,
            self.encoding
        )

        function = protocol_base.IntegerWrapper(
            function,
            8,
            self._bursts,
            self.encoding
        )
        d0 = protocol_base.IntegerWrapper(
            d0,
            8,
            self._bursts,
            self.encoding
        )

        f0 = protocol_base.IntegerWrapper(
            f0,
            8,
            self._bursts,
            self.encoding
        )
        d0_checksum, f0_checksum = self._calc_checksum(d0, f0)

        params = dict(
            D=d0,
            D_CHECKSUM=d0_checksum,
            F=f0,
            F_CHECKSUM=f0_checksum
        )
        packet1 = self._build_packet(**params)

        d_checksum, f_checksum = self._calc_checksum(device, function)

        params = dict(
            D=device,
            D_CHECKSUM=d_checksum,
            F=function,
            F_CHECKSUM=f_checksum
        )

        packet2 = self._build_packet(**params)
        params = dict(
            frequency=self.frequency,
            D=device,
            D0=d0,
            D_CHECKSUM=d_checksum,
            D0_CHECKSUM=d0_checksum,
            F=function,
            F0=f0,
            F_CHECKSUM=f_checksum,
            F0_CHECKSUM=f0_checksum
        )

        code = protocol_base.IRCode(
            self,
            packet1[:] + (packet2[:] * (repeat_count + 1)),
            [packet1[:]] + ([packet2[:]] * (repeat_count + 1)),
            params,
            repeat_count
        )

        return code
