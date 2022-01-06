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
from . import LeadOutError, DecodeError, RepeatLeadInError


TIMING = 605


class Anthem(protocol_base.IrProtocolBase):
    """
    IR decoder for the Anthem protocol.
    """
    irp = (
        '{38.0k,605,lsb}<1,-1|1,-3>((8000u,-4000u,D:8,S:8,F:8,C:8,1,-25m)2,'
        '8000u,-4000u,D:8,S:8,F:8,C:8,1,-75m)*{C=~(D+S+F+255):8}'
    )

    frequency = 38000
    bit_count = 32
    encoding = 'lsb'

    _lead_in = [8000, -4000]
    _lead_out1 = [TIMING, -25000]
    _lead_out2 = [TIMING, -75000]

    _bursts = [[TIMING, -TIMING], [TIMING, -TIMING * 3]]

    _code_order = [
        ['D', 8],
        ['S', 8],
        ['F', 8]
    ]

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

    _stored_codes = []

    @staticmethod
    def _calc_checksum(
        device: protocol_base.IntegerWrapper,
        sub_device: protocol_base.IntegerWrapper,
        function: protocol_base.IntegerWrapper
    ) -> protocol_base.IntegerWrapper:
        # C=~(D+S+F+255):8
        return (device + sub_device + function + 255)[True:8:0]

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        self._lead_out = self._lead_out1[:]
        try:
            code = protocol_base.IrProtocolBase.decode(self, data, frequency)
        except LeadOutError:
            self._lead_out = self._lead_out2[:]
            code = protocol_base.IrProtocolBase.decode(self, data, frequency)

        checksum = self._calc_checksum(
            code.device, 
            code.sub_device, 
            code.function
        )

        if checksum != code.checksum:
            raise DecodeError('Checksum failed')

        if self._lead_out == self._lead_out1:
            self._stored_codes.append(code)
            raise RepeatLeadInError
        elif len(self._stored_codes) == 2:
            new_code = self._stored_codes[0]
            new_code += self._stored_codes[1]
            del self._stored_codes[:]
            new_code += code
            code = new_code
        else:
            del self._stored_codes[:]
            raise RepeatLeadInError

        if self._last_code is not None:
            if self._last_code == code:
                return self._last_code

            self._last_code.repeat_timer.stop()

        self._last_code = code
        return code

    def encode(
        self,
        device: int,
        sub_device: int,
        function: int,
        repeat_count: int = 0
    ) -> protocol_base.IRCode:

        device = protocol_base.IntegerWrapper(
            device,
            8,
            self._bursts,
            self.encoding
        )
        sub_device = protocol_base.IntegerWrapper(
            sub_device,
            8,
            self._bursts,
            self.encoding
        )
        function = protocol_base.IntegerWrapper(
            function,
            8,
            self._bursts,
            self.encoding
        )

        checksum = self._calc_checksum(device, sub_device, function)

        lead_in = self._build_packet(
            D=device,
            S=sub_device,
            F=function,
            CHECKSUM=checksum,
        )
        lead_in.extend(self._lead_out1[:])

        code = self._build_packet(
            D=device,
            S=sub_device,
            F=function,
            CHECKSUM=checksum,
        )
        code.extend(self._lead_out2[:])

        params = dict(
            frequency=self.frequency,
            D=device,
            S=sub_device,
            F=function
        )

        code = protocol_base.IRCode(
            self,
            (lead_in[:] + lead_in[:] + code[:]) * (repeat_count + 1),
            ([lead_in[:]] + [lead_in[:]] + [code[:]]) * (repeat_count + 1),
            params,
            repeat_count
        )
        return code
