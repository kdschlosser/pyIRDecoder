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
from . import (
    DecodeError,
    RepeatLeadInError,
    TooManyBitsError,
    NotEnoughBitsError
)


TIMING = 182


class GuangZhou(protocol_base.IrProtocolBase):
    """
    IR decoder for the GuangZhou protocol.
    """
    irp = (
        '{38.0k,182,lsb}<3,-3|3,-6>(20,-10,T:2,D:6,F:8,S:8,20,-10,~T:2,D:6,'
        '~F:8,3,^108m,(20,-20,3,^108m)*){T=3}'
    )
    frequency = 38000
    bit_count = 40
    encoding = 'lsb'

    _lead_in = [TIMING * 20, -TIMING * 10]
    _lead_out = [TIMING * 3, 108000]
    _middle_timings = [(TIMING * 20, -TIMING * 10)]
    _bursts = [[TIMING * 3, -TIMING * 3], [TIMING * 3, -TIMING * 6]]

    _repeat_lead_in = [TIMING * 20, -TIMING * 20]
    _repeat_lead_out = [TIMING * 3, 108000]
    _repeat_bursts = []

    _code_order = [
        ['D', 6],
        ['F', 8],
        ['S', 8],
    ]

    _parameters = [
        ['T', 0, 1],
        ['D', 2, 7],
        ['F', 8, 15],
        ['S', 16, 23],
        ['T_CHECKSUM', 24, 25],
        ['D_CHECKSUM', 26, 31],
        ['F_CHECKSUM', 32, 39]

    ]
    # [D:0..63,F:0..255,S:0..255]
    encode_parameters = [
        ['device', 0, 63],
        ['sub_device', 0, 255],
        ['function', 0, 255],
    ]

    @staticmethod
    def _calc_checksum(
        device: protocol_base.IntegerWrapper,
        function: protocol_base.IntegerWrapper,
        toggle: protocol_base.IntegerWrapper
    ) -> Sequence[protocol_base.IntegerWrapper]:
        f = function[True:8:0]
        t = toggle[True:2:0]
        return device, f, t

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        try:
            code = protocol_base.IrProtocolBase.decode(self, data, frequency)

            if self._last_code is not None:
                if self._last_code == code:
                    return self._last_code

                self._last_code.repeat_timer.stop()
                self._last_code = None

            (
                dev_checksum,
                func_checksum,
                toggle_checksum
            ) = self._calc_checksum(code.device, code.function, code.toggle)

            if (
                dev_checksum != code.d_checksum or
                func_checksum != code.f_checksum or
                toggle_checksum != code.t_checksum
            ):
                raise DecodeError('Checksum failed')

            self._last_code = code
            return code
        except DecodeError:
            if self._sequence:
                rlc = self._sequence[0].original_rlc[:]
                rlc += data[:]
                del self._sequence[:]

                code = protocol_base.IrProtocolBase.decode(
                    self,
                    data,
                    frequency
                )

                if self._last_code is not None:
                    if self._last_code == code:
                        return self._last_code

                    self._last_code.repeat_timer.stop()
                    self._last_code = None

                (
                    dev_checksum,
                    func_checksum,
                    toggle_checksum
                ) = self._calc_checksum(
                    code.device,
                    code.function,
                    code.toggle
                )

                if (
                    dev_checksum != code.d_checksum or
                    func_checksum != code.f_checksum or
                    toggle_checksum != code.t_checksum
                ):
                    raise DecodeError('Checksum failed')

                self._last_code = code
                return code
            else:
                code = protocol_base.code_wrapper.CodeWrapper(
                    self.encoding,
                    self._lead_in[:],
                    list(self._middle_timings[0]),
                    [],
                    self._bursts[:],
                    self.tolerance,
                    data[:]
                )

                if code.num_bits > 24:
                    raise TooManyBitsError
                elif code.num_bits < 24:
                    raise NotEnoughBitsError

                params = dict(frequency=self.frequency)
                for name, start, stop in self._parameters[:4]:
                    params[name] = code.get_value(start, stop)

                code = protocol_base.IRCode(
                    self,
                    code.original_code,
                    list(code),
                    params
                )

                self._sequence.append(code)
                raise RepeatLeadInError

    def encode(
        self,
        device: int,
        sub_device: int,
        function: int,
        repeat_count: int = 0
    ) -> protocol_base.IRCode:

        device = protocol_base.IntegerWrapper(
            device,
            6,
            self._bursts,
            self.encoding
        )
        sub_device = protocol_base.IntegerWrapper(
            sub_device,
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
        toggle = protocol_base.IntegerWrapper(
            3,
            2,
            self._bursts,
            self.encoding
        )

        (
            dev_checksum,
            func_checksum,
            toggle_checksum
        ) = self._calc_checksum(device, function, toggle)

        packet = self._build_packet(
            toggle.timings,
            device.timings,
            function.timings,
            sub_device.timings,
            self._middle_timings[0],
            toggle_checksum.timings,
            dev_checksum.timings,
            func_checksum.timings,
        )

        params = dict(
            frequency=self.frequency,
            D=device,
            S=sub_device,
            F=function,
        )

        repeat = self._build_repeat_packet(repeat_count)

        code = protocol_base.IRCode(
            self,
            packet[:] + repeat[:],
            [packet[:]] + [repeat[:]],
            params,
            repeat_count
        )

        return code
