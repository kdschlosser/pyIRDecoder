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
from . import DecodeError, RepeatLeadOutError

TIMING = 889


class RC5x(protocol_base.IrProtocolBase):
    """
    IR decoder for the RC5x protocol.
    """
    irp = '{36k,889,msb}<1,-1|-1,1>(1,~S:1:6,(1-(T:1)),D:5,-4,S:6,F:6,^114m)*'
    frequency = 36000
    bit_count = 19
    encoding = 'msb'

    _lead_in = [TIMING]
    _lead_out = [114000]
    _middle_timings = [-TIMING * 4]
    _bursts = [[TIMING, -TIMING], [-TIMING, TIMING]]

    _has_repeat_lead_out = True

    _code_order = [
        ['D', 5],
        ['S', 6],
        ['F', 6],
    ]

    _parameters = [
        ['CHECKSUM', 0, 0],
        ['T', 1, 1],
        ['D', 2, 6],
        ['S', 7, 12],
        ['F', 13, 18]
    ]
    # [D:0..31,S:0..63,F:0..63,T@:0..1=0]
    encode_parameters = [
        ['device', 0, 31],
        ['sub_device', 0, 127],
        ['function', 0, 63]
    ]

    @staticmethod
    def _calc_checksum(
        sub_device: protocol_base.IntegerWrapper
    ) -> protocol_base.IntegerWrapper:
        return sub_device[True:1:6]

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)

        checksum = self._calc_checksum(code.sub_device)

        if checksum != code.checksum:
            raise DecodeError(str(checksum) + ' : ' + str(code.checksum))

        if self._last_code is not None:
            if (
                self._last_code == code and
                self._last_code.toggle == code.toggle
            ):
                return self._last_code

            last_code = self._last_code
            self._last_code.repeat_timer.stop()

            if last_code == code:
                raise RepeatLeadOutError

        self._last_code = code
        return code

    def encode(
        self,
        device: int,
        sub_device: int,
        function: int,
        repeat_count: int = 0
    ) -> protocol_base.IRCode:
        device = protocol_base.IntegerWrapper(
            device,
            5,
            self._bursts,
            self.encoding
        )
        sub_device = protocol_base.IntegerWrapper(
            sub_device,
            6,
            self._bursts,
            self.encoding
        )
        function = protocol_base.IntegerWrapper(
            function,
            6,
            self._bursts,
            self.encoding
        )
        toggle = protocol_base.IntegerWrapper(
            0,
            1,
            self._bursts,
            self.encoding
        )

        checksum = self._calc_checksum(sub_device)

        packet = self._build_packet(
            checksum.timings,
            toggle.timings,
            device.timings,
            self._middle_timings,
            sub_device[:6:0].timings,
            function.timings,
        )

        toggle = protocol_base.IntegerWrapper(
            1,
            1,
            self._bursts,
            self.encoding
        )

        lead_out = self._build_packet(
            checksum.timings,
            toggle.timings,
            device.timings,
            self._middle_timings,
            sub_device[:6:0].timings,
            function.timings,
        )

        params = dict(
            frequency=self.frequency,
            D=device,
            S=sub_device,
            F=function,
            CHECKSUM=checksum
        )

        code = protocol_base.IRCode(
            self,
            (packet[:] * (repeat_count + 1)) + lead_out[:],
            ([packet[:]] * (repeat_count + 1)) + [lead_out[:]],
            params,
            repeat_count
        )

        return code
