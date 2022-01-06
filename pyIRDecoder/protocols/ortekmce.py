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


TIMING = 480


class OrtekMCE(protocol_base.IrProtocolBase):
    """
    IR decoder for the OrtekMCE protocol.
    """
    irp = (
        '{38.6k,480,lsb}<1,-1|-1,1>'
        '([P=0][P=1][P=2],4,-1,D:5,P:2,F:6,C:4,-48m)+'
        '{C=3+#D+#P+#F}'
    )
    frequency = 38600
    bit_count = 17
    encoding = 'lsb'

    _lead_in = [TIMING * 4, -TIMING]
    _lead_out = [-48000]
    _middle_timings = []
    _bursts = [[TIMING, -TIMING], [-TIMING, TIMING]]

    _repeat_lead_in = []
    _repeat_lead_out = []
    _repeat_bursts = []

    _code_order = [
        ['D', 5],
        ['F', 6]
    ]

    _parameters = [
        ['D', 0, 4],
        ['P', 5, 6],
        ['F', 7, 12],
        ['CHECKSUM', 13, 16]
    ]
    # [D:0..31,F:0..63]
    encode_parameters = [
        ['device', 0, 31],
        ['function', 0, 63],
    ]

    @classmethod
    def _calc_checksum(
        cls,
        device: protocol_base.IntegerWrapper,
        function: protocol_base.IntegerWrapper,
        p: protocol_base.IntegerWrapper
    ) -> protocol_base.IntegerWrapper:
        c = protocol_base.IntegerWrapper(
            3 + device.num_one_bits + function.num_one_bits + p.num_one_bits,
            timings=cls._bursts,
            encoding=cls.encoding
        )

        return c[:4:0]

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        code = protocol_base.IrProtocolBase.decode(self, data, frequency)
        checksum = self._calc_checksum(code.device, code.function, code.p)

        if checksum != code.checksum or code.p not in (0, 1, 2):
            raise DecodeError('Checksum failed')

        if self._last_code is None:
            if code.p != 0:
                raise DecodeError('invalid start frame')

            self._last_code = code
            raise RepeatLeadInError

        if self._last_code.p == 0:
            if code.p != 1:
                raise DecodeError('invalid start frame')

            # noinspection PyProtectedMember
            self._last_code._normalized_rlc += [code._normalized_rlc[0]]
            # noinspection PyProtectedMember
            self._last_code._original_rlc += code._original_rlc
            # noinspection PyProtectedMember
            self._last_code._data['P'] = 1

            raise RepeatLeadInError

        if self._last_code.p == 1:
            if code.p != 2:
                raise DecodeError('invalid start frame')

            # noinspection PyProtectedMember
            self._last_code._normalized_rlc += [code._normalized_rlc[0]]
            # noinspection PyProtectedMember
            self._last_code._original_rlc += code._original_rlc
            # noinspection PyProtectedMember
            self._last_code._data['P'] = 2
            return self._last_code

        if (
            self._last_code.device == code.device and
            self._last_code.function == code.function
        ):
            if code.p == 2:
                return self._last_code

        elif code.p == 0:
            self._last_code.repeat_timer.stop()
            self._last_code = code

        raise RepeatLeadInError

    def encode(
        self,
        device: int,
        function: int,
        repeat_count: int = 0
    ):
        device = protocol_base.IntegerWrapper(
            device,
            5,
            self._bursts,
            self.encoding
        )
        function = protocol_base.IntegerWrapper(
            function,
            6,
            self._bursts,
            self.encoding
        )

        codes1 = []
        codes2 = []

        params = dict(
            D=device,
            F=function
        )
        
        for p in range(3):
            p = protocol_base.IntegerWrapper(
                p,
                2,
                self._bursts,
                self.encoding
            )

            params['P'] = p

            checksum = self._calc_checksum(
                device,
                function,
                p
            )
            params['CHECKSUM'] = checksum

            packet = self._build_packet(**params)
            codes1.extend(packet)
            codes2.append(packet)

        params['frequency'] = self.frequency

        code = protocol_base.IRCode(
            self,
            codes1 * (repeat_count + 1),
            codes2 * (repeat_count + 1),
            params,
            repeat_count
        )

        return code
