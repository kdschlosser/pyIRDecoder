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


TIMING = 444


class RC6632(protocol_base.IrProtocolBase):
    """
    IR decoder for the RC6632 protocol.
    """
    __name__ = 'RC6-6-32'

    irp = '{36k,444,msb}<-1,1|1,-1>(6,-2,1:1,6:3,-2,2,OEM1:8,S:8,(1-T):1,D:7,F:8,^107m)*{OEM1=128}'
    frequency = 36000
    bit_count = 36
    encoding = 'msb'

    _lead_in = [TIMING * 6, -TIMING * 2]
    _lead_out = [107000]
    _middle_timings = [(-TIMING * 2, TIMING * 2)]
    _bursts = [[-TIMING, TIMING], [TIMING, -TIMING]]

    _has_repeat_lead_out = True

    _code_order = [
        ['S', 8],
        ['D', 7],
        ['F', 8],
    ]

    _parameters = [
        ['C0', 0, 0],
        ['M', 1, 3],
        ['OEM1', 4, 11],
        ['S', 12, 19],
        ['T', 20, 20],
        ['D', 21, 27],
        ['F', 28, 35],
    ]
    # [D:0..127,S:0..255,F:0..255,T@:0..1=0]
    encode_parameters = [
        ['device', 0, 127],
        ['sub_device', 0, 255],
        ['function', 0, 255],
    ]

    def decode(self, data, frequency=0):
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)

        if self._last_code is not None:
            if (
                self._last_code == code and
                self._last_code.toggle == code.toggle
            ):
                return self._last_code

            last_code = self._last_code
            self._last_code.repeat_timer.stop()

            if last_code == code:
                raise RepeatLeadOut

        if code.c0 != 1:
            raise DecodeError('Checksum failed')

        if code.mode != 6:
            raise DecodeError('Incorrect Mode')

        if code.oem1 != 128:
            raise DecodeError('Incorrect OEM1 Code')

        if code.sub_device == 0x0F:
            raise DecodeError('MCE code')

        self._last_code = code
        return code

    def encode(self, device, sub_device, function, repeat_count=0):
        c0 = 1
        mode = 6
        oem1 = 128

        toggle = 0
        packet = self._build_packet(
            list(self._get_timing(c0, i) for i in range(1)),
            list(self._get_timing(mode, i) for i in range(3)),
            self._middle_timings[0],
            list(self._get_timing(oem1, i) for i in range(8)),
            list(self._get_timing(sub_device, i) for i in range(8)),
            list(self._get_timing(toggle, i) for i in range(1)),
            list(self._get_timing(device, i) for i in range(7)),
            list(self._get_timing(function, i) for i in range(8)),

        )

        toggle = 1
        lead_out = self._build_packet(
            list(self._get_timing(c0, i) for i in range(1)),
            list(self._get_timing(mode, i) for i in range(3)),
            self._middle_timings[0],
            list(self._get_timing(oem1, i) for i in range(8)),
            list(self._get_timing(sub_device, i) for i in range(8)),
            list(self._get_timing(toggle, i) for i in range(1)),
            list(self._get_timing(device, i) for i in range(7)),
            list(self._get_timing(function, i) for i in range(8)),

        )

        params = dict(
            frequency=self.frequency,
            D=device,
            S=sub_device,
            F=function
        )

        code = protocol_base.IRCode(
            self,
            [packet[:], lead_out[:]],
            ([packet[:]] * (repeat_count + 1)) + [lead_out[:]],
            params,
            repeat_count
        )

        return code

    def _test_decode(self):
        rlc = [[
            2664, -888, 444, -444, 444, -444, 444, -888, 444, -888, 1332, -888, 444, -444,
            444, -444, 444, -444, 444, -444, 444, -444, 444, -444, 444, -444, 888, -444, 444, -888,
            888, -888, 888, -888, 444, -444, 888, -888, 888, -888, 888, -888, 888, -444, 444, -888,
            444, -444, 444, -444, 444, -444, 444, -444, 444, -444, 444, -444, 444, -69704,
        ]]

        params = [dict(function=128, toggle=0, device=85, sub_device=106)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(function=128, toggle=0, device=85, sub_device=106)
        protocol_base.IrProtocolBase._test_encode(self, params)


RC6632 = RC6632()
