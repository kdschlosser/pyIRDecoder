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

MCE_COMMANDS = {
    0x00: "Number.0",
    0x01: "Number.1",
    0x02: "Number.2",
    0x03: "Number.3",
    0x04: "Number.4",
    0x05: "Number.5",
    0x06: "Number.6",
    0x07: "Number.7",
    0x08: "Number.8",
    0x09: "Number.9",
    0x0A: "Navigation.Escape",
    0x0B: "Navigation.Enter",
    0x0C: "Power.Toggle",
    0x0D: "Button.Start",
    0x0E: "Volume.Mute",
    0x0F: "Menu.Info",
    0x10: "Volume.Up",
    0x11: "Volume.Down",
    0x12: "Channel.Up",
    0x13: "Channel.Down",
    0x14: "Media.FastForward",
    0x15: "Media.Rewind",
    0x16: "Media.Play",
    0x17: "Media.Record",
    0x18: "Media.Pause",
    0x19: "Media.Stop",
    0x1A: "Media.Skip",
    0x1B: "Media.Replay",
    0x1C: "Number.Pound",
    0x1D: "Number.Star",
    0x1E: "Navigation.Up",
    0x1F: "Navigation.Down",
    0x20: "Navigation.Left",
    0x21: "Navigation.Right",
    0x22: "Navigation.Ok",
    0x23: "Navigation.Back",
    0x24: "Menu.DVD",
    0x25: "Source.LiveTV",
    0x26: "Menu.Guide",
    0x27: "Video.Aspect",
    0x46: "Source.TV",
    0x47: "Source.Music",
    0x48: "Source.RecordedTV",
    0x49: "Source.Pictures",
    0x4A: "Source.Videos",
    0x4C: "Source.Audio",
    0x4D: "Button.Subtitle",
    0x50: "Source.Radio",
    0x5A: "Button.Teletext",
    0x5B: "Button.Red",
    0x5C: "Button.Green",
    0x5D: "Button.Yellow",
    0x5E: "Button.Blue",
}


OEM1 = 0x80
OEM2 = 0x0F
MCE_DEVICE = 0x04


TIMING = 444


class MCE(protocol_base.IrProtocolBase):
    """
    IR decoder for the RC6632 protocol.
    """
    irp = '{36k,444,msb}<-1,1|1,-1>((6,-2,1:1,6:3,-2,2,OEM1:8,S:8,T:1,D:7,F:8,^107m)*,T=1-T) {OEM1=128}'
    frequency = 36000
    bit_count = 36
    encoding = 'msb'

    _lead_in = [TIMING * 6, -TIMING * 2]
    _lead_out = [107000]
    _middle_timings = [(-TIMING * 2, TIMING * 2)]
    _bursts = [[-TIMING, TIMING], [TIMING, -TIMING]]

    _code_order = [
        ['F', 8],
    ]

    _parameters = [
        ['C0', 0, 0],
        ['M', 1, 3],
        ['OEM1', 4, 11],
        ['OEM2', 12, 19],
        ['T', 20, 20],
        ['D', 21, 27],
        ['F', 28, 35],
    ]
    # [D:0..127,S:0..255,F:0..255,T@:0..1=0]
    encode_parameters = [
        ['function', 0, 0x5E],
    ]

    _has_repeat_lead_out = True

    @property
    def function(self):
        return list(MCE_COMMANDS.keys())

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

        if (
            code.c0 != 1 or
            code.mode != 6 or
            code.oem1 != OEM1 or
            code.oem2 != OEM2 or
            code.device != MCE_DEVICE
        ):
            raise DecodeError('Checksum failed')

        if code.function not in MCE_COMMANDS:
            raise DecodeError('Invalid function')

        code.name = self.__class__.__name__ + '.' + MCE_COMMANDS[code.function]

        self._last_code = code
        return code

    def encode(self, function, repeat_count=0):
        c0 = 1
        mode = 6
        oem1 = OEM1
        oem2 = OEM2
        device = MCE_DEVICE
        toggle = 1

        code = self._build_packet(
            list(self._get_timing(c0, i) for i in range(1)),
            list(self._get_timing(mode, i) for i in range(3)),
            self._middle_timings[0],
            list(self._get_timing(oem1, i) for i in range(8)),
            list(self._get_timing(oem2, i) for i in range(8)),
            list(self._get_timing(toggle, i) for i in range(1)),
            list(self._get_timing(device, i) for i in range(7)),
            list(self._get_timing(function, i) for i in range(8)),
        )

        toggle = 0

        lead_out = self._build_packet(
            list(self._get_timing(c0, i) for i in range(1)),
            list(self._get_timing(mode, i) for i in range(3)),
            self._middle_timings[0],
            list(self._get_timing(oem1, i) for i in range(8)),
            list(self._get_timing(oem2, i) for i in range(8)),
            list(self._get_timing(toggle, i) for i in range(1)),
            list(self._get_timing(device, i) for i in range(7)),
            list(self._get_timing(function, i) for i in range(8)),
        )

        packet = [code] * (repeat_count + 1)
        packet += [lead_out]

        params = dict(
            frequency=self.frequency,
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
        rlc = self.encode(0x0B)
        params = [dict(function=0x0B)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(function=208, toggle=1)
        protocol_base.IrProtocolBase._test_encode(self, params)


MCE = MCE()
