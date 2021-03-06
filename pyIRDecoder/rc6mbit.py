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
from . import DecodeError, RepeatLeadOut, EncodeError

try:
    long = long
except NameError:
    long = int


TIMING = 444


class RC6MBIT(protocol_base.IrProtocolBase):
    """
    IR decoder for the RC6MBIT protocol.
    """
    irp = '{36k,444,msb}<-1,1|1,-1>(6,-2,1:1,M:3,<-2,2|2,-2>(1-(T:1)),CODE:??,??)*'
    frequency = 36000
    bit_count = 64
    encoding = 'msb'

    _lead_in = [TIMING * 6, -TIMING * 2]
    _lead_out = [-999999999999]
    _middle_timings = [{'start': 4, 'stop': 5, 'bursts': [[-TIMING * 2, TIMING * 2], [TIMING * 2, -TIMING * 2]]}]
    _bursts = [[-TIMING, TIMING], [TIMING, -TIMING]]

    _has_repeat_lead_out = True

    _parameters = [
        ['C0', 0, 0],
        ['M', 1, 3],
        ['T', 4, 4],
        ['CODE', 5, -1]
    ]
    # [OEM1:0..255,OEM2:0..255,D:0..255,F:0..255,M:0..7,T@:0..1=0]
    encode_parameters = [
        ['mode', 0, 7],
        ['code', 0, long('1' * 64, 2)]
    ]

    def decode(self, data, frequency=0):
        c = protocol_base.code_wrapper.CodeWrapper(
            self.encoding,
            self._lead_in[:],
            self._lead_out[:],
            self._middle_timings[:],
            self._bursts[:],
            self.tolerance,
            data[:]
        )

        c0 = c.get_value(0, 0)
        mode = c.get_value(1, 3)
        toggle = c.get_value(4, 4)
        x = c._decoded_code[5:]

        num_bits = len(x)
        if num_bits > self.bit_count:
            raise DecodeError('Protocol is limited to 64 bits')

        x = ''.join(str(bit) for bit in x)
        x = long(x, 2)

        params = dict(
            frequency=self.frequency,
            C0=c0,
            CODE=x,
            M=mode,
            T=toggle,
        )

        code = protocol_base.IRCode(
            self,
            c.original_code,
            list(c),
            params
        )

        hex_code = hex(x)[2:].upper()
        hex_code = hex_code.zfill(len(hex_code) + (len(hex_code) % 2))
        code.name = 'RC6-' + str(code.mode) + '-' + str(num_bits) + '.0' + str(code.mode) + ':' + hex_code

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

        self._last_code = code
        return code

    def encode(self, mode, code, repeat_count=0):
        c0 = 1

        if code > long('1' * 64, 2):
            raise EncodeError('code is to large')

        c = bin(code)[2:]
        code_len = len(c)

        packet = self._build_packet(
            list(self._get_timing(c0, i) for i in range(1)),
            list(self._get_timing(mode, i) for i in range(3)),
            [-TIMING * 2, TIMING * 2],
            list(self._get_timing(code, i) for i in range(code_len))
        )

        if packet[-1] == self._lead_out[0]:
            packet = packet[:-1]

        else:
            packet[-1] -= self._lead_out[0]

        tt = sum(abs(item) for item in packet)

        space = -(107000 - tt)
        if packet[-1] < 0:
            packet[-1] += space
        else:
            packet += [space]

        lead_out = self._build_packet(
            list(self._get_timing(c0, i) for i in range(1)),
            list(self._get_timing(mode, i) for i in range(3)),
            [TIMING * 2, -TIMING * 2],
            list(self._get_timing(code, i) for i in range(code_len))
        )

        if lead_out[-1] == self._lead_out[0]:
            lead_out = lead_out[:-1]

        else:
            lead_out[-1] -= self._lead_out[0]

        tt = sum(abs(item) for item in lead_out)

        space = -(107000 - tt)
        if lead_out[-1] < 0:
            lead_out[-1] += space
        else:
            lead_out += [space]

        hex_code = hex(code)[2:].upper()
        hex_code = hex_code.zfill(len(hex_code) + (len(hex_code) % 2))

        params = dict(
            frequency=self.frequency,
            M=mode,
            CODE=code
        )

        code = protocol_base.IRCode(
            self,
            [packet[:], lead_out[:]],
            ([packet[:]] * (repeat_count + 1)) + [lead_out[:]],
            params,
            repeat_count
        )

        code.name = 'RC6-' + str(code.mode) + '-' + str(code_len) + '.0' + str(code.mode) + ':' + hex_code

        return code

    def _test_decode(self):
        return
        rlc = [[
            2664, -888, 444, -444, 444, -444, 444, -888, 444, -888, 888, -444, 444, -444,
            444, -444, 444, -444, 888, -888, 444, -444, 888, -444, 444, -888, 444, -444, 444, -444,
            888, -888, 444, -444, 888, -888, 888, -888, 444, -444, 888, -888, 888, -444, 444, -888,
            444, -444, 444, -444, 444, -444, 444, -444, 444, -444, 444, -444, 888, -70148,
        ]]

        params = [dict(function=1, toggle=0, device=75, oem2=137, oem1=9, mode=6)]

        return protocol_base.IrProtocolBase._test_decode(self, rlc, params)

    def _test_encode(self):
        return
        params = dict(function=1, toggle=0, device=75, oem2=137, oem1=9, mode=6)
        protocol_base.IrProtocolBase._test_encode(self, params)


RC6MBIT = RC6MBIT()
