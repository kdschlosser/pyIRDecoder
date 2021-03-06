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
from . import DecodeError, EncodeError, RepeatLeadOut


REMOTE_SUBDEVICE = 0x0C
REMOTE = {
    0x01: 'Number.1',
    0x02: 'Number.2',
    0x03: 'Number.3',
    0x04: 'Number.4',
    0x05: 'Number.5',
    0x06: 'Number.6',
    0x07: 'Number.7',
    0x08: 'Number.8',
    0x09: 'Number.9',
    0x00: 'Number.0',
    0x0C: 'Power.Toggle',
    0x20: 'Channel.Up',
    0x21: 'Channel.Down',
    0x24: 'Media.Pause',
    0x28: 'Media.FastForward',
    0x3C: 'Button.Text',
    0x3D: 'Media.Rewind',
    0x3E: 'Media.Play',
    0x3F: 'Media.Stop',
    0x40: 'Media.Record',
    0x83: 'Navigation.Back',
    0x58: 'Navigation.Up',
    0x59: 'Navigation.Down',
    0x5A: 'Navigation.Left',
    0x5B: 'Navigation.Right',
    0x5C: 'Navigation.Select',
    0xCB: 'Media.Info',
    0x6D: 'Button.Red',
    0x6E: 'Button.Green',
    0x6F: 'Button.Yellow',
    0x70: 'Button.Blue',
    0x7D: 'Button.BoxOffice',
    0x7E: 'Button.Services',
    0x80: 'Button.Sky',
    0x81: 'Button.Help',
    0x84: 'Source.TV',
    0xCC: 'Button.TVGuide',
    0xF5: 'Button.Interactive',
}

KEYBOARD_SUBDEVICE = 0x02
KEYBOARD = {
    0x0C: 'Power.Toggle',
    0x20: 'Channel.Up',
    0x21: 'Channel.Down',
    0x5D: 'Navigation.Left',
    0x5E: 'Navigation.Right',
    0x5F: 'Navigation.Up',
    0x60: 'Navigation.Down',
    0x61: 'Navigation.Select',
    0x62: 'Button.Help',
    0x63: 'Button.Text',
    0x64: 'Media.Info',
    0x65: 'Navigation.Backup',
    0x66: 'Button.Red',
    0x67: 'Button.Green',
    0x68: 'Button.Yellow',
    0x69: 'Button.Blue',
    0x7D: 'Button.BoxOffice',
    0x7E: 'Button.Services',
    0x80: 'Button.Sky',
    0x84: 'Source.TV',
    0x88: 'Key.Home',
    0x89: 'Key.Delete',
    0x8A: 'Key.End',
    0x8B: 'Key.PageUp',
    0x8C: 'Key.PageDown',
    0x8D: 'Key.Escape',
    0x8E: 'Key.Tab',
    0x8F: 'Key.Return',
    0x90: 'Key.BackSpace',
    0x91: 'Key.Space',
    0x96: 'Letter.a',
    0x97: 'Letter.b',
    0x98: 'Letter.c',
    0x99: 'Letter.d',
    0x9A: 'Letter.e',
    0x9B: 'Letter.f',
    0x9C: 'Letter.g',
    0x9D: 'Letter.h',
    0x9E: 'Letter.i',
    0x9F: 'Letter.j',
    0xA0: 'Letter.k',
    0xA1: 'Letter.l',
    0xA2: 'Letter.m',
    0xA3: 'Letter.n',
    0xA4: 'Letter.o',
    0xA5: 'Letter.p',
    0xA6: 'Letter.q',
    0xA7: 'Letter.r',
    0xA8: 'Letter.s',
    0xA9: 'Letter.t',
    0xAA: 'Letter.u',
    0xAB: 'Letter.v',
    0xAC: 'Letter.w',
    0xAD: 'Letter.x',
    0xAE: 'Letter.y',
    0xAF: 'Letter.z',
    0xB0: 'Letter.A',
    0xB1: 'Letter.B',
    0xB2: 'Letter.C',
    0xB3: 'Letter.D',
    0xB4: 'Letter.E',
    0xB5: 'Letter.F',
    0xB6: 'Letter.G',
    0xB7: 'Letter.H',
    0xB8: 'Letter.I',
    0xB9: 'Letter.J',
    0xBA: 'Letter.K',
    0xBB: 'Letter.L',
    0xBC: 'Letter.M',
    0xBD: 'Letter.N',
    0xBE: 'Letter.O',
    0xBF: 'Letter.P',
    0xC0: 'Letter.Q',
    0xC1: 'Letter.R',
    0xC2: 'Letter.S',
    0xC3: 'Letter.T',
    0xC4: 'Letter.U',
    0xC5: 'Letter.V',
    0xC6: 'Letter.W',
    0xC7: 'Letter.X',
    0xC8: 'Letter.Y',
    0xC9: 'Letter.Z',
    0xCC: 'Button.TVGuide',
    0xD1: 'Key.Euro',
    0xD2: 'Key.!',
    0xD3: 'Key."',
    0xD4: 'Key.Pound',
    0xD5: 'Key.$',
    0xD6: 'Key.%',
    0xD7: 'Key.^',
    0xD8: 'Key.&',
    0xD9: 'Key.*',
    0xDA: 'Key.(',
    0xDB: 'Key.)',
    0xDC: 'Key._',
    0xDD: 'Key.-',
    0xDE: 'Key.+',
    0xDF: 'Key.=',
    0xE0: 'Key.{',
    0xE1: 'Key.}',
    0xE2: 'Key.[',
    0xE3: 'Key.]',
    0xE4: 'Key.:',
    0xE5: 'Key.;',
    0xE6: 'Key.@',
    0xE7: 'Key.\'',
    0xE8: 'Key.~',
    0xE9: 'Key.#',
    0xEA: 'Key.<',
    0xEB: 'Key.>',
    0xEC: 'Key.,',
    0xED: 'Key..',
    0xEE: 'Key.?',
    0xEF: 'Key./',
    0xF0: 'Key.\\',
    0xF1: 'Key.|',
    0xF5: 'Button.Interactive',
    0xF6: 'Number.0',
    0xF7: 'Number.1',
    0xF8: 'Number.2',
    0xF9: 'Number.3',
    0xFA: 'Number.4',
    0xFB: 'Number.5',
    0xFC: 'Number.6',
    0xFD: 'Number.7',
    0xFE: 'Number.8',
    0xFF: 'Number.0',
}

TIMING = 444

SKY_PLUS = 0x00


class SkyPlus(protocol_base.IrProtocolBase):
    """
    IR decoder for the SkyPlus protocol.
    """
    irp = '{36k,444,msb}<-1,1|1,-1>(6,-2,1:1,6:3,<-2,2|2,-2>(1-(T:1)),D:12,F:8,-100m)*'
    frequency = 36000
    bit_count = 25
    encoding = 'msb'

    _lead_in = [TIMING * 6, -TIMING * 2]
    _lead_out = [-100000]
    _middle_timings = [{'start': 4, 'stop': 5, 'bursts': [[-TIMING * 2, TIMING * 2], [TIMING * 2, -TIMING * 2]]}]
    _bursts = [[-TIMING, TIMING], [TIMING, -TIMING]]

    _has_repeat_lead_out = True

    _code_order = [
        ['F', 18],
    ]

    _parameters = [
        ['C0', 0, 0],
        ['M', 1, 3],
        ['T', 4, 4],
        ['D', 5, 16],
        ['F', 17, 24],
    ]
    # [D:0..255,S:0..15,F:0..255,T@:0..1=0]
    encode_parameters = [
        ['function', 0, 255],
    ]

    @property
    def function(self):
        res = []

        for function in REMOTE.keys():
            function |= REMOTE_SUBDEVICE << 8
            res += [function]

        for function in KEYBOARD.keys():
            function |= KEYBOARD_SUBDEVICE << 8
            res += [function]

        return res

    def decode(self, data, frequency=0):
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)

        if code.c0 != 1 or code.mode != 6:
            raise DecodeError('Checksum failed')

        if code.device not in (REMOTE_SUBDEVICE, KEYBOARD_SUBDEVICE):
            raise DecodeError('Not a sky device')

        if code.device == REMOTE_SUBDEVICE:
            if code.function not in REMOTE:
                raise DecodeError('Unknown remote key')

            code.name = '{0}.Remote.{1}'.format(self.__class__.__name__, REMOTE[code.function])
        else:
            if code.function not in KEYBOARD:
                raise DecodeError('Unknown keyboard key')

            code.name = '{0}.Keyboard.{1}'.format(self.__class__.__name__, KEYBOARD[code.function])

        code._data['F'] |= code.device << 8

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

    def encode(self, function, repeat_count=0):
        c0 = 1
        mode = 6

        device = function >> 8
        func = function & 0xFF

        if device not in (REMOTE_SUBDEVICE, KEYBOARD_SUBDEVICE):
            raise EncodeError('Not a sky device')

        if device == REMOTE_SUBDEVICE:
            if func not in REMOTE:
                raise EncodeError('Unknown remote key')

            name = '{0}.Remote.{1}'.format(self.__class__.__name__, REMOTE[func])

        else:
            if func not in KEYBOARD:
                raise EncodeError('Unknown keyboard key')

            name = '{0}.Keyboard.{1}'.format(self.__class__.__name__, KEYBOARD[func])

        code = self._build_packet(
            list(self._get_timing(c0, i) for i in range(1)),
            list(self._get_timing(mode, i) for i in range(3)),
            [-TIMING * 2, TIMING * 2],
            list(self._get_timing(device, i) for i in range(12)),
            list(self._get_timing(func, i) for i in range(8)),

        )
        lead_out = self._build_packet(
            list(self._get_timing(c0, i) for i in range(1)),
            list(self._get_timing(mode, i) for i in range(3)),
            [TIMING * 2, -TIMING * 2],
            list(self._get_timing(device, i) for i in range(12)),
            list(self._get_timing(func, i) for i in range(8)),

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

        code.name = name

        return code

    def _test_decode(self):
        params = [dict(function=0x7D), None]
        function = REMOTE_SUBDEVICE << 8 | 0x7D
        rlc = self.encode(function)

        protocol_base.IrProtocolBase._test_decode(self, rlc, params)

        params = [dict(function=0x97), None]
        function = KEYBOARD_SUBDEVICE << 8 | 0x97
        rlc = self.encode(function)

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        params = dict(function=40, toggle=1, device=138, sub_device=5)
        protocol_base.IrProtocolBase._test_encode(self, params)


SkyPlus = SkyPlus()
