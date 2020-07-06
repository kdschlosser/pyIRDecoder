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
from . import DecodeError, RepeatLeadIn


TIMING = 605


class Anthem(protocol_base.IrProtocolBase):
    """
    IR decoder for the Anthem protocol.
    """
    irp = (
        '{38.0k,605,lsb}<1,-1|1,-3>((8000u,-4000u,D:8,S:8,F:8,C:8,1,-25m)2,8000u,-4000u,D:8,S:8,F:8,C:8,1,-)* '
        '{C=~(D+S+F+255):8}'
    )

    frequency = 38000
    bit_count = 32
    encoding = 'lsb'

    _lead_in = [8000, -4000]
    _lead_out = [TIMING, -25000]
    _middle_timings = []
    _bursts = [[TIMING, -TIMING], [TIMING, -TIMING * 3]]

    _repeat_lead_in = [TIMING * 16, -TIMING * 4]
    _repeat_lead_out = [TIMING, 108000]
    _repeat_bursts = []

    _parameters = [
        ['D', 0, 7],
        ['S', 8, 15],
        ['F', 16, 23],
        ['CHECKSUM', 24, 31],
    ]
    # [D:0..255,S:0..255,F:0..255]
    encode_parameters = [
        ['device', 0, 255],
        ['sub_device', 0, 255],
        ['function', 0, 255],
    ]

    _packet_count = 0

    def _calc_checksum(self, device, sub_device, function):
        # C=~(D+S+F+255):8
        c = self._get_bits(device + sub_device + function + 255, 0, 7)
        return self._invert_bits(c, 8)

    def decode(self, data, frequency=0):
        try:
            code = protocol_base.IrProtocolBase.decode(self, data, frequency)
        except DecodeError:
            self._lead_out[1] = -25000
            self._packet_count = 0
            raise

        checksum = self._calc_checksum(code.device, code.sub_device, code.function)

        if checksum != code.checksum:
            self._packet_count = 0
            self._lead_out[1] = -25000
            raise DecodeError('Checksum failed')

        if self._packet_count <= 1:
            self._packet_count += 1
            if self._packet_count == 2:
                self._lead_out[1] = -TIMING * 100

            raise RepeatLeadIn

        self._lead_out[1] = -25000
        self._packet_count = 0
        return code

    def encode(self, device, sub_device, function):

        _lead_out = self._lead_out[1]

        self._lead_out[1] = -25000

        checksum = self._calc_checksum(device, sub_device, function)

        lead_in = self._build_packet(
            list(self._get_timing(device, i) for i in range(8)),
            list(self._get_timing(sub_device, i) for i in range(8)),
            list(self._get_timing(function, i) for i in range(8)),
            list(self._get_timing(checksum, i) for i in range(8)),
        )

        self._lead_out[1] = -TIMING * 100

        packet = self._build_packet(
            list(self._get_timing(device, i) for i in range(8)),
            list(self._get_timing(sub_device, i) for i in range(8)),
            list(self._get_timing(function, i) for i in range(8)),
            list(self._get_timing(checksum, i) for i in range(8)),
        )

        self._lead_out[1] = _lead_out

        return [lead_in, lead_in, packet]

    def _test_decode(self):
        rlc = [
            [
                +8000, -4000, +605, -605, +605, -1815, +605, -1815, +605, -605, +605, -1815, +605, -1815, +605, -605,
                +605, -605, +605, -605, +605, -1815, +605, -605, +605, -1815, +605, -1815, +605, -1815, +605, -1815,
                +605, -1815, +605, -1815, +605, -605, +605, -1815, +605, -1815, +605, -1815, +605, -605, +605, -605,
                +605, -1815, +605, -1815, +605, -1815, +605, -605, +605, -605, +605, -1815, +605, -1815, +605, -605,
                +605, -605, +605, -25000
            ],
            [
                +8000, -4000, +605, -605, +605, -1815, +605, -1815, +605, -605, +605, -1815, +605, -1815, +605, -605,
                +605, -605, +605, -605, +605, -1815, +605, -605, +605, -1815, +605, -1815, +605, -1815, +605, -1815,
                +605, -1815, +605, -1815, +605, -605, +605, -1815, +605, -1815, +605, -1815, +605, -605, +605, -605,
                +605, -1815, +605, -1815, +605, -1815, +605, -605, +605, -605, +605, -1815, +605, -1815, +605, -605,
                +605, -605, +605, -25000
            ],
            [
                +8000, -4000, +605, -605, +605, -1815, +605, -1815, +605, -605, +605, -1815, +605, -1815, +605, -605,
                +605, -605, +605, -605, +605, -1815, +605, -605, +605, -1815, +605, -1815, +605, -1815, +605, -1815,
                +605, -1815, +605, -1815, +605, -605, +605, -1815, +605, -1815, +605, -1815, +605, -605, +605, -605,
                +605, -1815, +605, -1815, +605, -1815, +605, -605, +605, -605, +605, -1815, +605, -1815, +605, -605,
                +605, -605, +605, -60500
            ]
        ]

        params = [None, None, dict(function=157, sub_device=250, device=54)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(function=97, sub_device=52, device=46)
        protocol_base.IrProtocolBase._test_encode(self, params)


Anthem = Anthem()