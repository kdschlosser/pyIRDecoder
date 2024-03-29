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


TIMING = 330


class Zaptor36(protocol_base.IrProtocolBase):
    """
    IR decoder for the Zaptor36 protocol.
    """
    irp = (
        '{36k,330,msb}<-1,1|1,-1>([T=0][T=1],8,-6,2,D:8,'
        'T:1,S:7,F:8,E:4,C:4,-74m)'
        '{C=(D:4+D:4:4+S:4+S:3:4+8*T+F:4+F:4:4+E)&15}'
    )
    frequency = 36000
    bit_count = 32
    encoding = 'msb'

    _lead_in = [TIMING * 8, -TIMING * 6, TIMING * 2]
    _lead_out = [-74000]
    _bursts = [[-TIMING, TIMING], [TIMING, -TIMING]]

    _has_repeat_lead_out = True

    _code_order = [
        ['D', 8],
        ['S', 7],
        ['F', 8],
        ['E', 4]
    ]

    _parameters = [
        ['D', 0, 7],
        ['T', 8, 8],
        ['S', 9, 15],
        ['F', 16, 23],
        ['E', 24, 27],
        ['CHECKSUM', 28, 31]
    ]
    # [D:0..255,S:0..127,F:0..127,E:0..15]
    encode_parameters = [
        ['device', 0, 255],
        ['sub_device', 0, 127],
        ['function', 0, 255],
        ['extended_function', 0, 15]
    ]

    @staticmethod
    def _calc_checksum(
        device: protocol_base.IntegerWrapper,
        sub_device: protocol_base.IntegerWrapper,
        toggle: protocol_base.IntegerWrapper,
        function: protocol_base.IntegerWrapper,
        extended_function: protocol_base.IntegerWrapper
    ) -> protocol_base.IntegerWrapper:
        # {C=(D:4+D:4:4+S:4+S:3:4+8*T+F:4+F:4:4+E)&15}
        c = (
            device[:4:0] +
            device[:4:4] +
            sub_device[:4:0] +
            sub_device[:3:4] +
            (8 * toggle) +
            function[:4:0] +
            function[:4:4] +
            extended_function
        ) & 15
        return c[:4:0]

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)

        checksum = self._calc_checksum(
            code.device,
            code.sub_device,
            code.toggle,
            code.function,
            code.extended_function
        )

        if checksum != code.checksum:
            raise DecodeError('Invalid checksum')

        if self._last_code is not None:
            if self._last_code == code:
                if code.toggle == 1:
                    self._last_code.repeat_timer.stop()

                return self._last_code

            self._last_code.repeat_timer.stop()

        if code.toggle == 1:
            return code

        self._last_code = code
        return code

    def encode(
        self,
        device: int,
        sub_device: int,
        function: int,
        extended_function: int,
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
            7,
            self._bursts,
            self.encoding
        )
        function = protocol_base.IntegerWrapper(
            function,
            8,
            self._bursts,
            self.encoding
        )
        extended_function = protocol_base.IntegerWrapper(
            extended_function,
            4,
            self._bursts,
            self.encoding
        )

        if repeat_count == 0:
            toggle = protocol_base.IntegerWrapper(
                1,
                1,
                self._bursts,
                self.encoding
            )
        else:
            toggle = protocol_base.IntegerWrapper(
                0,
                1,
                self._bursts,
                self.encoding
            )

        checksum = self._calc_checksum(
            device,
            sub_device,
            toggle,
            function,
            extended_function
        )
        params = dict(
            D=device,
            S=sub_device,
            F=function,
            E=extended_function,
            T=toggle,
            CHECKSUM=checksum
        )

        code = self._build_packet(**params)

        if repeat_count > 0:
            toggle = protocol_base.IntegerWrapper(
                1,
                1,
                self._bursts,
                self.encoding
            )

            checksum = self._calc_checksum(
                device,
                sub_device,
                toggle,
                function,
                extended_function
            )

            params['T'] = toggle
            params['CHECKSUM'] = checksum

            lead_out = self._build_packet(**params)
            params['frequency'] = self.frequency

            code = protocol_base.IRCode(
                self,
                (code[:] * repeat_count) + lead_out[:],
                ([code[:]] * repeat_count) + [lead_out[:]],
                params,
                repeat_count
            )
        else:
            params['frequency'] = self.frequency

            code = protocol_base.IRCode(
                self,
                code[:],
                [code[:]],
                params,
                repeat_count
            )

        return code
