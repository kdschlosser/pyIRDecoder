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
from . import DecodeError, RepeatLeadOutError, EncodeError

STREAMZAP = {
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
    0x0A: "Button.Power",
    0x0B: "Audio.Volume.Mute",
    0x0C: "Channel.Up",
    0x0D: "Audio.Volume.Up",
    0x0E: "Channel.Down",
    0x0F: "Audio.Volume.Down",
    0x10: "Navigation.Up",
    0x11: "Navigation.Left",
    0x12: "Navigation.OK",
    0x13: "Navigation.Right",
    0x14: "Navigation.Down",
    0x15: "Button.Menu",
    0x16: "Navigation.Exit",
    0x17: "Media.Play",
    0x18: "Media.Pause",
    0x19: "Media.Stop",
    0x1A: "Media.SkipBack",
    0x1B: "Media.SkipForward",
    0x1C: "Media.Record",
    0x1D: "Media.Rewind",
    0x1E: "Media.FastForward",
    0x20: "Button.Red",
    0x21: "Button.Green",
    0x22: "Button.Yellow",
    0x23: "Button.Blue",
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
        ['CHECKSUM', 0, 0],
        ['T', 1, 1],
        ['D', 2, 7],
        ['F', 8, 13]
    ]
    # [D:0..63,F:0..63,T:0..1]
    encode_parameters = [
        ['device', 0, 63],
        ['function', 0, 63],
    ]

    @staticmethod
    def _calc_checksum(
        function: protocol_base.IntegerWrapper
    ) -> protocol_base.IntegerWrapper:
        return function[True:1:6]

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)

        checksum = self._calc_checksum(code.function)

        if checksum != code.checksum:
            raise DecodeError('Checksum failed')

        if code.function in STREAMZAP:
            code.name = '{0}.{1}.{2}'.format(
                self.__class__.__name__,
                hex(int(code.device))[2:].upper().zfill(2),
                STREAMZAP[code.function]
            )

        if self._last_code is not None:
            if (
                self._last_code == code and
                self._last_code.toggle == code.toggle
            ):
                return self._last_code

            last_code = self._last_code
            self._last_code.repeat_timer.stop()

            if last_code == code:
                raise RepeatLeadOutError

        self._last_code = code
        return code

    def encode(
        self,
        device: int,
        function: int,
        repeat_count: int = 0
    ) -> protocol_base.IRCode:
        if function in STREAMZAP:
            name = '{0}.{1}.{2}'.format(
                self.__class__.__name__,
                hex(device)[2:].upper().zfill(2),
                STREAMZAP[function]
            )
        else:
            raise EncodeError('Not a valid function ({0})'.format(function))

        function = protocol_base.IntegerWrapper(
            function,
            6,
            self._bursts,
            self.encoding
        )

        checksum = self._calc_checksum(function)

        params = dict(
            D=device,
            F=function,
            T=0,
            CHECKSUM=checksum
        )
        packet = self._build_packet(**params)
        params['T'] = 1
        lead_out = self._build_packet(**params)

        params['frequency'] = self.frequency

        code = protocol_base.IRCode(
            self,
            (packet[:] * (repeat_count + 1)) + lead_out[:],
            ([packet[:]] * (repeat_count + 1)) + [lead_out[:]],
            params,
            repeat_count
        )

        code.name = name

        return code
