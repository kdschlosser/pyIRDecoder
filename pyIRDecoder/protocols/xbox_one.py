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
from . import DecodeError


XBOX_ONE_DEVICE = 0x01
XBOX_ONE_SUBDEVICE = 0xD8

XBOX_ONE_COMMANDS = {
    0x00: 'Number.0',
    0x80: 'Number.1',
    0x40: 'Number.2',
    0xC0: 'Number.3',
    0x20: 'Number.4',
    0xA0: 'Number.5',
    0x60: 'Number.6',
    0xE0: 'Number.7',
    0x10: 'Number.8',
    0x90: 'Number.9',
    0x66: 'Button.A',
    0xA6: 'Button.B',
    0x16: 'Button.X',
    0xE6: 'Button.Y',
    0xF8: 'Navigation.Down',
    0x04: 'Navigation.Left',
    0x84: 'Navigation.Right',
    0x78: 'Navigation.Up',
    0xD0: 'Navigation.Enter',
    0xC4: 'Navigation.Exit',
    0x44: 'Navigation.OK',
    0xF6: 'Button.Menu',
    0x68: 'Media.Play',
    0x18: 'Media.Pause',
    0x0E: 'Media.Play/Pause',
    0x28: 'Media.FastForward',
    0xA8: 'Media.Rewind',
    0x98: 'Media.Stop',
    0xD8: 'Media.SkipBack',
    0x58: 'Media.SkipForward',
    0x08: 'Volume.Up',
    0x88: 'Volume.Down',
    0x70: 'Volume.Mute',
    0x48: 'Channel.Up',
    0xC8: 'Channel.Down',
    0x76: 'Button.View',
    0x14: 'Media.Eject',
    0x30: 'Power.Toggle1',
    0x94: 'Power.Toggle2',
    0xF4: 'Power.Toggle3',
    0x26: 'Button.XBOX'
}


TIMING = 564


class XBoxOne(protocol_base.IrProtocolBase):
    """
    IR decoder for the XBoxOne protocol.
    """
    irp = (
        '{38.4k,564,lsb}<1,-1|1,-3>'
        '(8,-8,D:8,S:8,F:8,~F:8,1,^108m,(8,-8,D:1,1,^108m)*)'
    )
    frequency = 38400
    bit_count = 32
    encoding = 'lsb'

    _lead_in = [TIMING * 8, -TIMING * 8]
    _lead_out = [TIMING, 108000]
    _middle_timings = []
    _bursts = [[TIMING, -TIMING], [TIMING, -TIMING * 3]]

    _repeat_lead_in = [TIMING * 8, -TIMING * 8]
    _repeat_lead_out = [TIMING, 108000]
    _repeat_bursts = [[TIMING, -TIMING], [TIMING, -TIMING * 3]]

    _code_order = [
        ['F', 8],
    ]

    _parameters = [
        ['D', 0, 7],
        ['S', 8, 15],
        ['F', 16, 23],
        ['CHECKSUM', 24, 31],
    ]
    # [D:0..255,S:0..255=255-D,F:0..255]
    encode_parameters = [
        ['function', 0, 255],
    ]

    @property
    def function(self):
        return list(XBOX_ONE_COMMANDS.keys())

    @staticmethod
    def _calc_checksum(
        function: protocol_base.IntegerWrapper
    ) -> protocol_base.IntegerWrapper:
        return function[True:8:0]

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)

        if self._last_code is not None:
            # noinspection PyProtectedMember
            if (
                self._last_code == code and
                code._code.get_value(0, 0) == code.device[0]
            ):
                return self._last_code

            last_code = self._last_code
            self._last_code.repeat_timer.stop()

            if last_code == code:
                raise DecodeError('invalid repeat')

        func_checksum = self._calc_checksum(code.function)

        if func_checksum != code.checksum:
            raise DecodeError('Checksum failed')

        if (
            code.device != XBOX_ONE_DEVICE or
            code.sub_device != XBOX_ONE_SUBDEVICE
        ):
            raise DecodeError('Not an XBoxOne')

        if code.function in XBOX_ONE_COMMANDS:
            code.name = (
                self.__class__.__name__ + '.' +
                XBOX_ONE_COMMANDS[code.function]
            )

        self._last_code = code
        return code

    def encode(
        self,
        function: int,
        repeat_count: int = 0
    ) -> protocol_base.IRCode:
        function = protocol_base.IntegerWrapper(
            function,
            8,
            self._bursts,
            self.encoding
        )

        checksum = self._calc_checksum(function)

        params = dict(
            D=XBOX_ONE_DEVICE,
            S=XBOX_ONE_SUBDEVICE,
            F=function,
            CHECKSUM=checksum
        )
        device = protocol_base.IntegerWrapper(
            params['D'],
            1,
            self._bursts,
            self.encoding
        )

        packet = self._build_packet(**params)
        repeat = self._build_packet(device.timings)

        params['frequency'] = self.frequency

        code = protocol_base.IRCode(
            self,
            packet[:] + (repeat * repeat_count),
            [packet[:]] + ([repeat] * repeat_count),
            params,
            repeat_count
        )

        if function in XBOX_ONE_COMMANDS:
            code.name = (
                self.__class__.__name__ + '.' +
                XBOX_ONE_COMMANDS[function]
            )

        return code
