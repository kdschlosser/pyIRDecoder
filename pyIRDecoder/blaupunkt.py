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
from . import (
    DecodeError,
    RepeatLeadIn,
    RepeatLeadOut,
    RepeatTimeoutExpired
)


TIMING = 512


class Blaupunkt(protocol_base.IrProtocolBase):
    """
    IR decoder for the Blaupunkt protocol.
    """
    irp = '{30.3k,512,lsb}<-1,1|1,-1>(1,-5,1023:10,-44,(1,-5,1:1,F:6,D:3,-236)+,1,-5,1023:10,-44)'
    frequency = 30300
    bit_count = 10
    encoding = 'lsb'

    _lead_in = [TIMING, -TIMING * 5]
    _lead_out = [-TIMING * 44]
    _bursts = [[-TIMING, TIMING], [TIMING, -TIMING]]

    _code_order = [
        ['F', 6],
        ['D', 3]
    ]

    _parameters = [
        ['C0', 0, 0],
        ['F', 1, 6],
        ['D', 7, 9]
    ]
    # [F:0..63,D:0..7]
    encode_parameters = [
        ['device', 0, 7],
        ['function', 0, 63],
    ]

    _has_repeat_lead_out = True

    def __init__(self, parent=None, xml=None):
        protocol_base.IrProtocolBase.__init__(self, parent, xml)
        if xml is None:
            self._enabled = False

    def decode(self, data, frequency=0):
        try:
            code = protocol_base.IrProtocolBase.decode(self, data, frequency)
        except DecodeError:
            if self._lead_out[0] == -TIMING * 44:
                self._lead_out[0] = -TIMING * 236
                code = protocol_base.IrProtocolBase.decode(self, data, frequency)
            else:
                self._lead_out[0] = -TIMING * 44
                code = protocol_base.IrProtocolBase.decode(self, data, frequency)

        if self._last_code is not None:
            if self._last_code == code:
                return self._last_code

            self._last_code.repeat_timer.stop()
            self._last_code = None

        if self._lead_out[0] == -TIMING * 44:
            if code.c0 != 1 or code.device != 7 or code.function != 63:
                raise DecodeError('Invalid repeat lead in/out')

            raise RepeatLeadOut

        if code.c0 != 1:
            raise DecodeError('Invalid checksum')

        self._last_code = code
        return code

    def encode(self, device, function, repeat_count=0):
        c0 = 1
        d = 7
        f = 63

        _lead_out = self._lead_out[0]

        self._lead_out[0] = -TIMING * 44

        lead_in = self._build_packet(
            list(self._get_timing(c0, i) for i in range(1)),
            list(self._get_timing(d, i) for i in range(3)),
            list(self._get_timing(f, i) for i in range(6))
        )

        self._lead_out[0] = -TIMING * 236

        code = self._build_packet(
            list(self._get_timing(c0, i) for i in range(1)),
            list(self._get_timing(function, i) for i in range(6)),
            list(self._get_timing(device, i) for i in range(3))
        )

        self._lead_out[0] = -TIMING * 44

        lead_out = self._build_packet(
            list(self._get_timing(c0, i) for i in range(1)),
            list(self._get_timing(d, i) for i in range(3)),
            list(self._get_timing(f, i) for i in range(6))
        )

        self._lead_out[0] = _lead_out

        packet = [lead_in, code]
        packet += [code] * repeat_count
        packet += [lead_out]

        params = dict(
            frequency=self.frequency,
            D=device,
            F=function,
        )

        code = protocol_base.IRCode(
            self,
            [lead_in[:], code[:], lead_out[:]],
            packet[:],
            params,
            repeat_count
        )
        return code

    def _test_decode(self):
        rlc = [
            [
                +512, -2560, +512, -512, +512, -512, +512, -512, +512, -512, +512, -512, +512, -512, +512, -512, +512,
                -512, +512, -512, +512, -23040
            ],
            [
                +512, -2560, +512, -512, +512, -1024, +1024, -1024, +512, -512, +512, -512, +1024, -512, +512, -1024,
                +512, -120832
            ],
            [
                +512, -2560, +512, -512, +512, -512, +512, -512, +512, -512, +512, -512, +512, -512, +512, -512, +512,
                -512, +512, -512, +512, -23040
            ],
        ]

        params = [
            None,
            dict(device=3, function=5),
            None
        ]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(device=3, function=5)
        protocol_base.IrProtocolBase._test_encode(self, params)


Blaupunkt = Blaupunkt()
