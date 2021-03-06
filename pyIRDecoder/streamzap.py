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
from . import EncodeError, DecodeError, RepeatLeadOut

STREAMZAP = {
    0x00: "Num0",
    0x01: "Num1",
    0x02: "Num2",
    0x03: "Num3",
    0x04: "Num4",
    0x05: "Num5",
    0x06: "Num6",
    0x07: "Num7",
    0x08: "Num8",
    0x09: "Num9",
    0x0A: "Power",
    0x0B: "Mute",
    0x0C: "ChannelUp",
    0x0D: "VolumeUp",
    0x0E: "ChannelDown",
    0x0F: "VolumeDown",
    0x10: "Up",
    0x11: "Left",
    0x12: "Ok",
    0x13: "Right",
    0x14: "Down",
    0x15: "Menu",
    0x16: "Exit",
    0x17: "Play",
    0x18: "Pause",
    0x19: "Stop",
    0x1A: "PreviousTrack",
    0x1B: "NextTrack",
    0x1C: "Record",
    0x1D: "Rewind",
    0x1E: "Forward",
    0x20: "Red",
    0x21: "Green",
    0x22: "Yellow",
    0x23: "Blue",
}

TIMING = 889


class StreamZap(protocol_base.IrProtocolBase):
    """
    IR decoder for the StreamZap protocol.
    """
    irp = '{36k,889,msb}<1,-1|-1,1>(1,~F:1:6,T:1,D:6,F:6,^114m)*'
    frequency = 36000
    bit_count = 14
    encoding = 'msb'

    _lead_in = [TIMING]
    _lead_out = [114000]
    _middle_timings = []
    _bursts = [[TIMING, -TIMING], [-TIMING, TIMING]]

    _has_repeat_lead_out = True

    _code_order = [
        ['D', 6],
        ['F', 6],
    ]

    _parameters = [
        ['F_CHECKSUM', 0, 0],
        ['T', 1, 1],
        ['D', 2, 7],
        ['F', 8, 13]
    ]
    # [D:0..63,F:0..63,T:0..1]
    encode_parameters = [
        ['device', 0, 63],
        ['function', 0, 63],
    ]

    def __init__(self, parent=None, xml=None):
        protocol_base.IrProtocolBase.__init__(self, parent, xml)
        if xml is None:
            self._enabled = False

    def _calc_checksum(self, function):
        f = int(not self._get_bit(function, 5))
        return f

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

        func_checksum = self._calc_checksum(code.function)

        if func_checksum != code.f_checksum:
            raise DecodeError('Checksum failed')

        if code.function in STREAMZAP:
            code.name = '{0}.{1}.{2}'.format(
                self.__class__.__name__,
                hex(code.device)[2:].upper().zfill(2),
                STREAMZAP[code.function]
            )

        self._last_code = code
        return code

    def encode(self, device, function, repeat_count=0):
        func_checksum = self._calc_checksum(function)
        toggle = 0

        code = self._build_packet(
            list(self._get_timing(func_checksum, i) for i in range(1)),
            list(self._get_timing(toggle, i) for i in range(1)),
            list(self._get_timing(device, i) for i in range(6)),
            list(self._get_timing(function, i) for i in range(6)),
        )

        toggle = 1

        lead_out = self._build_packet(
            list(self._get_timing(func_checksum, i) for i in range(1)),
            list(self._get_timing(toggle, i) for i in range(1)),
            list(self._get_timing(device, i) for i in range(6)),
            list(self._get_timing(function, i) for i in range(6)),
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

        if function in STREAMZAP:
            code.name = '{0}.{1}.{2}'.format(
                self.__class__.__name__,
                hex(device)[2:].upper().zfill(2),
                STREAMZAP[function]
            )

        return code

    def _test_decode(self):
        rlc = self.encode(30, 0x0B, 1)
        params = [dict(device=30, function=0x0B, toggle=1)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(function=10, toggle=1, device=51)
        protocol_base.IrProtocolBase._test_encode(self, params)


StreamZap = StreamZap()
