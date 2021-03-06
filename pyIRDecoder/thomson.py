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
from . import RepeatLeadOut


TIMING = 500


class Thomson(protocol_base.IrProtocolBase):
    """
    IR decoder for the Thomson protocol.
    """
    irp = '{33k,500,lsb}<1,-4|1,-9>(D:4,(1-T):1,D:1:4,F:6,1,^80m)*'
    frequency = 33000
    bit_count = 12
    encoding = 'lsb'

    _lead_in = []
    _lead_out = [TIMING, 80000]
    _middle_timings = []
    _bursts = [[TIMING, -TIMING * 4], [TIMING, -TIMING * 9]]

    _has_repeat_lead_out = True

    _code_order = [
        ['D', 4],
        ['F', 6],
    ]

    # D:4,(1-T):1,D:1:4,F:6
    _parameters = [
        ['D', 0, 3],
        ['T', 4, 4],
        ['D1', 5, 5],
        ['F', 6, 11],
    ]
    # [D:0..31,F:0..63,T@:0..1=0]
    encode_parameters = [
        ['device', 0, 31],
        ['function', 0, 63],
    ]

    def decode(self, data, frequency=0):
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)

        params = dict(
            D=self._set_bit(code.device, 4, self._get_bit(code.d1, 0)),
            F=code.function,
            CHECKSUM=code.checksum,
            T=code.toggle,
            frequency=self.frequency
        )

        code = protocol_base.IRCode(self, code.original_rlc, code.normalized_rlc, params)
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

        self._last_code = code
        return code

    def encode(self, device, function, repeat_count=0):
        d1 = self._get_bit(device, 4)

        toggle = 0

        code = self._build_packet(
            list(self._get_timing(device, i) for i in range(4)),
            list(self._get_timing(toggle, i) for i in range(1)),
            list(self._get_timing(d1, i) for i in range(1)),
            list(self._get_timing(function, i) for i in range(6))
        )
        toggle = 1
        lead_out = self._build_packet(
            list(self._get_timing(device, i) for i in range(4)),
            list(self._get_timing(toggle, i) for i in range(1)),
            list(self._get_timing(d1, i) for i in range(1)),
            list(self._get_timing(function, i) for i in range(6))
        )

        packet = [code] * (repeat_count + 1)
        packet += [lead_out]

        params = dict(
            frequency=self.frequency,
            D=device,
            F=function,
        )

        code = protocol_base.IRCode(
            self,
            [code[:], lead_out[:]],
            packet[:],
            params,
            repeat_count
        )

        return code

    def _test_decode(self):
        rlc = [[
            500, -2000, 500, -2000, 500, -4500, 500, -4500, 500, -2000, 500, -2000, 500, -4500, 
            500, -2000, 500, -2000, 500, -2000, 500, -2000, 500, -4500, 500, -39500, 
        ]]

        params = [dict(function=33, toggle=0, device=12)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(function=33, toggle=0, device=12)
        protocol_base.IrProtocolBase._test_encode(self, params)


Thomson = Thomson()
