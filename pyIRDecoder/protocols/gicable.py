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
from . import DecodeError, LeadOutError, LeadInError


TIMING = 490


class GICable(protocol_base.IrProtocolBase):
    """
    IR decoder for the GICable protocol.
    """
    irp = (
        '{38.7k,490,lsb}<1,-4.5|1,-9>(18,-9,F:8,D:4,C:4,1,-84,'
        '(18,-4.5,1,-178)*){C=-(D+F:4+F:4:4)}'
    )
    frequency = 38700
    bit_count = 16
    encoding = 'lsb'

    _lead_in = [TIMING * 18, -TIMING * 9]
    _lead_out = [TIMING, -TIMING * 84]
    _middle_timings = []
    _bursts = [
        [TIMING, int(-TIMING * 4.5)],
        [TIMING, -TIMING * 9]
    ]

    _repeat_lead_in = [TIMING * 18, int(-TIMING * 4.5)]
    _repeat_lead_out = [TIMING, -TIMING * -178]
    _repeat_bursts = []

    _code_order = [
        ['F', 8],
        ['D', 4]
    ]

    _parameters = [
        ['F', 0, 7],
        ['D', 8, 11],
        ['CHECKSUM', 12, 15]
    ]

    # [D:0..15,F:0..255]
    encode_parameters = [
        ['device', 0, 15],
        ['function', 0, 255],
    ]

    @staticmethod
    def _calc_checksum(
        device: protocol_base.IntegerWrapper,
        function: protocol_base.IntegerWrapper
    ) -> protocol_base.IntegerWrapper:
        # -(D+F:4+F:4:4)
        c = -(device + function[:4:0] + function[:4:4])
        return c[:4:0]

    def _c_leadout(self, data: list, lead_out: list, bursts: list) -> bool:
        if lead_out and lead_out[-1] > 0:
            tt = sum(abs(item) for item in data)
            if not self._match(tt, lead_out[1]):
                return False

            data.pop(len(data) - 1)
            start = len(lead_out) - 2

        elif lead_out:
            start = len(lead_out) - 1
        else:
            return True

        for i in range(start, -1, -1):
            timing = lead_out[i]
            burst = data.pop(len(data) - 1)
            if not self._match(burst, timing):
                if i != 0 or burst < 0 < timing or burst > 0 > timing:
                    return False

                for burst_timings in bursts:
                    if (
                        (
                            burst_timings[-1] < 0 > timing or
                            burst_timings[-1] > 0 < timing
                        )
                        and self._match(burst, timing + burst_timings[-1])
                    ):
                        data.append(burst_timings[-1])
                        break
                else:
                    return False

        return True

    def _check_leadout(self, data: list) -> bool:
        return self._c_leadout(
            data,
            self._lead_out,
            self._bursts
        )

    def _c_lead_in(self, data: list, lead_in: list, bursts: list) -> bool:
        for i, timing in enumerate(lead_in):
            burst = data.pop(0)
            if not self._match(burst, timing):
                if (
                    i != len(lead_in) - 1 or
                    burst < 0 < timing or
                    burst > 0 > timing
                ):
                    return False

                for burst_timings in bursts:
                    if (
                        (
                            burst_timings[0] < 0 > timing or
                            burst_timings[0] > 0 < timing
                        )
                        and self._match(burst, timing + burst_timings[0])
                    ):
                        data.insert(0, burst_timings[0])
                        break
                else:
                    return False

        return True

    def _check_leadin(self, data: list) -> bool:
        return self._c_lead_in(
            data,
            self._lead_in,
            self._bursts
        )

    def _check_repeat_leadin(self, data: list) -> bool:
        return self._c_lead_in(
            data,
            self._repeat_lead_in,
            self._repeat_bursts
        )

    def _check_repeat_leadout(self, data: list) -> bool:
        return self._c_leadout(
            data,
            self._repeat_lead_out,
            self._repeat_bursts
        )

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        code = data[:]

        if self._last_code is not None:
            if self._check_repeat_leadout(code):
                if self._check_repeat_leadin(code):
                    return self._last_code
                else:
                    self._last_code.repeat_timer.stop()
                    self._last_code = None
                    code = data[:]
            else:
                self._last_code = None
                code = data[:]

        if not self._check_leadout(code):
            raise LeadOutError

        if not self._check_leadin(code):
            raise LeadInError(str(data))

        code = protocol_base.IrProtocolBase.decode(self, data, frequency)
        checksum = self._calc_checksum(code.device, code.function)

        if checksum != code.checksum:
            raise DecodeError('Checksum failed')

        self._last_code = code
        return code

    def encode(
        self,
        device: int,
        function: int,
        repeat_count: int = 0
    ) -> protocol_base.IRCode:
        device = protocol_base.IntegerWrapper(
            device, 
            4, 
            self._bursts,
            self.encoding
        )
        function = protocol_base.IntegerWrapper(
            function,
            8,
            self._bursts,
            self.encoding
        )

        checksum = self._calc_checksum(device, function)
        params = dict(
            D=device,
            F=function,
            CHECKUM=checksum
        )

        packet = self._build_packet(
            function.timings,
            device.timings,
            checksum.timings
        )
        params['frequency'] = self.frequency

        repeat = self._repeat_lead_in[:] + self._repeat_lead_out[:]

        code = protocol_base.IRCode(
            self,
            packet[:] + (repeat[:] * (repeat_count + 1)),
            [packet[:]] + ([repeat[:]] * (repeat_count + 1)),
            params,
            repeat_count
        )
        return code
