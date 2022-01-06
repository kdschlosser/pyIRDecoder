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
from . import DecodeError, RepeatLeadInError


class SolidTek16(protocol_base.IrProtocolBase):
    """
    IR decoder for the SolidTek16 protocol.
    """
    irp = (
        '{38k}<-624,468|468,-624>'
        '(S=0,(1820,-590,0:1,D:4,F:7,S:1,C:4,1:1,-143m,S=1)3) '
        '{C= F:4:0 + F:3:4 + 8*S } '
    )

    frequency = 38000
    bit_count = 18
    encoding = 'lsb'

    _lead_in = [1820, -590]
    _lead_out = [-143000]
    _middle_timings = []
    _bursts = [[-624, 468], [468, -624]]

    repeat_timeout = (
        sum(abs(item) for item in _lead_in) +
        (sum(abs(item) for item in _bursts[0]) * bit_count) +
        abs(_lead_out[0])
    ) * 3

    _code_order = [
        ['D', 4],
        ['F', 7],
    ]

    _parameters = [
        ['C0', 0, 0],
        ['D', 1, 4],
        ['F', 5, 11],
        ['S', 12, 12],
        ['CHECKSUM', 13, 16],
        ['C1', 17, 17]
    ]

    # [D:0..15, F:0..127]
    encode_parameters = [
        ['device', 0, 15],
        ['function', 0, 127],
    ]

    _sequence = []

    @staticmethod
    def _calc_checksum(
        function: protocol_base.IntegerWrapper,
        s: protocol_base.IntegerWrapper
    ) -> protocol_base.IntegerWrapper:
        # {C = F:4:0 + F:3:4 + 8 * S}
        c = function[:4:0] + function[:3:4] + 8 * s
        return c[:4:0]

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)
        checksum = self._calc_checksum(code.function, code.s)

        if checksum != code.checksum or code.c0 != 0 or code.c1 != 1:
            raise DecodeError(str(code.c0) + ' : ' + str(code.c1))

        if len(self._sequence) == 1:
            if code.s != 1:
                del self._sequence[:]
                raise DecodeError('Invalid checksum')

            self._sequence.append(code)
            raise RepeatLeadInError

        elif len(self._sequence) == 2:
            if code.s != 1:
                del self._sequence[:]
                raise DecodeError('Invalid checksum')

            code1 = self._sequence[0]
            code2 = self._sequence[1]
            code3 = code
            del self._sequence[:]

            if code1.device == code2.device == code3.device:
                if code1.function == code2.function == code3.function:
                    pass
                else:
                    raise DecodeError('Device mismatch')
            else:
                raise DecodeError('Device mismatch')
            # noinspection PyProtectedMember
            code1._original_rlc += code2._original_rlc + code3._original_rlc
            # noinspection PyProtectedMember
            code1._normalized_rlc += (
                code2._normalized_rlc + code3._normalized_rlc
            )
            code = code1

        elif code.s != 0:
            raise DecodeError('Invalid checksum')

        else:
            self._sequence.append(code)
            raise RepeatLeadInError

        if self._last_code is not None:
            if self._last_code == code:
                return self._last_code

            self._last_code.repeat_timer.stop()
            self._last_code = None

        self._last_code = code
        return code

    def encode(
        self,
        device: int,
        function: int,
        repeat_count: int = 0
    ) -> protocol_base.IRCode:
        function = protocol_base.IntegerWrapper(
            function,
            7,
            self._bursts,
            self.encoding
        )

        s = protocol_base.IntegerWrapper(
            0,
            1,
            self._bursts,
            self.encoding
        )

        checksum = self._calc_checksum(function, s)

        params = dict(
            D=device,
            F=function,
            S=s,
            CHECKSUM=checksum,
            C0=0,
            C1=1
        )

        packet = self._build_packet(**params)

        s = protocol_base.IntegerWrapper(
            1,
            1,
            self._bursts,
            self.encoding
        )

        checksum = self._calc_checksum(function, s)

        params['CHECKSUM'] = checksum
        params['S'] = s

        lead_out = self._build_packet(**params)

        params['frequency'] = self.frequency

        code = protocol_base.IRCode(
            self,
            packet[:] + lead_out[:] + lead_out[:] * (repeat_count + 1),
            [packet[:], lead_out[:], lead_out[:]] * (repeat_count + 1),
            params,
            repeat_count
        )

        return code
