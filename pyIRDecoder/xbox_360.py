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
from . import DecodeError, RepeatLeadOut
from . import protocol_base


XBOX360_COMMANDS = {
    0x00: 'Number.0',
    0x01: 'Number.1',
    0x03: 'Number.3',
    0x05: 'Number.5',
    0x07: 'Number.7',
    0x09: 'Number.9',
    0x0C: 'Power.Toggle',
    0x0F: 'Button.Info',
    0x12: 'Channel.Up',
    0x14: 'Media.FastForward',
    0x16: 'Media.Play',
    0x17: 'Media.Record',
    0x18: 'Media.Pause',
    0x1A: 'Media.Next',
    0x1C: 'Button.Reload',
    0x1F: 'Navigation.Down',
    0x20: 'Navigation.Left',
    0x24: 'Menu.DVD',
    0x26: 'Button.Y',
    0x28: 'Button.OpenCloseTray',
    0x4F: 'Button.Display',
    0x66: 'Button.A',
    0x02: 'Number.2',
    0x04: 'Number.4',
    0x06: 'Number.6',
    0x08: 'Number.8',
    0x0A: 'Button.Clear',
    0x0B: 'Navigation.Enter',
    0x0D: 'Button.Start',
    0x0E: 'Volume.Mute',
    0x10: 'Voluem.Down',
    0x11: 'Volume.Up',
    0x13: 'Channel.Down',
    0x15: 'Media.Rewind',
    0x19: 'Media.Toggle',
    0x1B: 'Media.Previous',
    0x1D: 'Button.100',
    0x1E: 'Navigation.Up',
    0x21: 'Navigation.Right',
    0x22: 'Navigation.Ok',
    0x23: 'Navigation.Back',
    0x25: 'Button.B',
    0x51: 'Button.Title',
    0x64: 'Button.Xbox',
    0x68: 'Button.X'
}

OEM1 = 0x80
OEM2 = 0x0F

XBOX1_DEVICE = 0x74

TIMING = 444


class XBox360(protocol_base.IrProtocolBase):
    """
    IR decoder for the RC6632 protocol.
    """
    irp = '{36k,444,msb}<-1,1|1,-1>(6,-2,1:1,6:3,-2,2,OEM1:8,OEM2:8,(1-T):1,D:7,F:8,^107m)*{OEM1=0x80,OEM2=0x0F,D=0x74||0xF4}'
    frequency = 36000
    bit_count = 36
    encoding = 'msb'

    _lead_in = [TIMING * 6, -TIMING * 2]
    _lead_out = [107000]
    _middle_timings = [(-TIMING * 2, TIMING * 2)]
    _bursts = [[-TIMING, TIMING], [TIMING, -TIMING]]

    _has_repeat_lead_out = True

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
        ['function', 0, 255],
    ]

    @property
    def function(self):
        return list(XBOX360_COMMANDS.keys())

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
            raise DecodeError('Incorrect mode')

        if code.oem1 != OEM1 or code.OEM2 != OEM2:
            raise DecodeError('Incorrect oem')

        if code.device != XBOX1_DEVICE:
            raise DecodeError('device is not an XBox360')

        if code.function in XBOX360_COMMANDS:
            code.name = self.__class__.__name__ + '.' + XBOX360_COMMANDS[code.function]

        self._last_code = code
        return code

    def encode(self, function, repeat_count=0):
        c0 = 1
        mode = 6
        oem1 = OEM1
        oem2 = OEM2
        device = XBOX1_DEVICE

        toggle = 0
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

        toggle = 1
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

        if function in XBOX360_COMMANDS:
            code.name = self.__class__.__name__ + '.' + XBOX360_COMMANDS[function]

        return code

    def _test_decode(self):
        rlc = self.encode(0x1C)
        params = [dict(function=0x1C), None]
        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(function=128, toggle=0, device=85, sub_device=106)
        protocol_base.IrProtocolBase._test_encode(self, params)


XBox360 = XBox360()
