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


TIMING = 444


class RC6M28(protocol_base.IrProtocolBase):
    """
    IR decoder for the RC6M28 protocol.
    """
    __name__ = 'RC6-m-28'

    irp = (
        '{36k,444,msb}<-1,1|1,-1>'
        '(6,-2,1:1,M:3,<-2,2|2,-2>(1-(T:1)),D:8,S:12,F:8,-100m)*'
    )
    frequency = 36000
    bit_count = 33
    encoding = 'msb'

    _lead_in = [TIMING * 6, -TIMING * 2]
    _lead_out = [-100000]
    _middle_timings = [{
        'start': 4,
        'stop': 5,
        'bursts': [[-TIMING * 2, TIMING * 2], [TIMING * 2, -TIMING * 2]]
    }]
    _bursts = [[-TIMING, TIMING], [TIMING, -TIMING]]

    _has_repeat_lead_out = True

    _code_order = [
        ['M', 3],
        ['D', 8],
        ['S', 12],
        ['F', 8]
    ]

    _parameters = [
        ['C0', 0, 0],
        ['M', 1, 3],
        ['T', 4, 4],
        ['D', 5, 12],
        ['S', 13, 24],
        ['F', 25, 32],
    ]
    # [D:0..255,S:0..4095,F:0..255,M:0..7,T@:0..1=0]
    encode_parameters = [
        ['mode', 0, 7],
        ['device', 0, 255],
        ['sub_device', 0, 4095],
        ['function', 0, 255],
    ]

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)

        if code.c0 != 1:
            raise DecodeError('Checksum failed')

        if self._last_code is not None:
            if (
                self._last_code == code and
                self._last_code.toggle == code.toggle
            ):
                return self._last_code

            last_code = self._last_code
            self._last_code.repeat_timer.stop()

            # if last_code == code:
            #     raise RepeatLeadOutError

        self._last_code = code

        return code

    def encode(
        self,
        mode: int,
        device: int,
        sub_device: int,
        function: int,
        repeat_count: int = 0
    ) -> protocol_base.IRCode:

        c0 = protocol_base.IntegerWrapper(
            1,
            1,
            self._bursts,
            self.encoding
        )
        mode = protocol_base.IntegerWrapper(
            mode,
            3,
            self._bursts,
            self.encoding
        )

        device = protocol_base.IntegerWrapper(
            device,
            8,
            self._bursts,
            self.encoding
        )
        sub_device = protocol_base.IntegerWrapper(
            sub_device,
            12,
            self._bursts,
            self.encoding
        )
        function = protocol_base.IntegerWrapper(
            function,
            8,
            self._bursts,
            self.encoding
        )

        packet = self._build_packet(
            c0.timings,
            mode.timings,
            [-TIMING * 2, TIMING * 2],
            device.timings,
            sub_device.timings,
            function.timings,

        )
        lead_out = self._build_packet(
            c0.timings,
            mode.timings,
            [TIMING * 2, -TIMING * 2],
            device.timings,
            sub_device.timings,
            function.timings,
        )

        params = dict(
            frequency=self.frequency,
            D=device,
            S=sub_device,
            F=function,
            C0=c0,
            M=mode
        )

        code = protocol_base.IRCode(
            self,
            (packet[:] * (repeat_count + 1)) + lead_out[:],
            ([packet[:]] * (repeat_count + 1)) + [lead_out[:]],
            params,
            repeat_count
        )

        return code
