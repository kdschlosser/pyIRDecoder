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
from .. import LeadOutError, LeadInError

TIMING = 895


class AdNotham(protocol_base.IrProtocolBase):
    """
    IR decoder for the AdNotham protocol.
    """

    [[895, -1790, 1790, -895, 895, -895, 895, -1790, 895, -895, 895, -895, 1790, -1790, 895, -895, 1790, -1790, 1790, -89835]]
    
    irp = '{35.7k,895,msb}<1,-1|-1,1>(1,-2,1,D:6,F:6,^114m)*'
    frequency = 35700
    bit_count = 12
    encoding = 'msb'

    _lead_in = [TIMING, -TIMING * 2, TIMING]
    _lead_out = [114000]
    _bursts = [[TIMING, -TIMING], [-TIMING,  TIMING]]

    _code_order = [
        ['D', 6],
        ['F', 6]
    ]

    _parameters = [
        ['D', 0, 5],
        ['F', 6, 11],
    ]
    # [D:0..63,F:0..63]
    encode_parameters = [
        ['device', 0, 63],
        ['function', 0, 63],
    ]

    # def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
    #     code = data[:]
    #     original_code = data[:]
    #     normalized_code = []
    #
    #     tt = sum(abs(item) for item in code)
    #
    #     if not self._match(tt, self._lead_out[0]):
    #         raise LeadOutError
    #
    #     if not self._match_sequence(code[:2], self._lead_in[:2]):
    #         raise LeadInError
    #
    #     code = code[2:]
    #     original_code.extend(self._lead_in[:2])
    #
    #     if self._match(code[0], self._lead_in[-1]):
    #         code = code[1:]
    #     else:
    #         for timings in self._bursts:
    #             if self._match(timings[0] + self._lead_in[-1], code[0]):
    #                 code = code[1:]
    #                 code.insert(0, timings[0])
    #                 break
    #         else:
    #             raise LeadInError
    #
    #     normalized_code.append(self._lead_in)
    #
    #     n_code, decoded = self._decode_manchester(code)
    #     normalized_code += n_code
    #
    #     tt = sum(abs(item) for item in normalized_code)
    #     normalized_code.append(self._lead_out[-1] - tt)
    #
    #     params = dict(frequency=self.frequency)
    #     for param, start, stop in self._parameters:
    #         value = 0
    #         for i in range(start, stop + 1):
    #             value |= decoded[i] << ~i + stop + 1
    #
    #         params[param] = value
    #
    #     code = protocol_base.IRCode(
    #         self,
    #         original_code,
    #         normalized_code,
    #         params
    #     )
    #
    #     if self._last_code is not None:
    #         if self._last_code == code:
    #             return self._last_code
    #
    #         self._last_code.repeat_timer.stop()
    #         self._last_code = None
    #
    #     self._last_code = code
    #     return code

    def encode(self, device, function, repeat_count=0):
        packet = self._build_packet(
            D=device,
            F=function,
        )

        params = dict(
            frequency=self.frequency,
            D=device,
            F=function
        )

        code = protocol_base.IRCode(
            self,
            packet[:] * (repeat_count + 1),
            [packet[:]] * (repeat_count + 1),
            params,
            repeat_count
        )
        return code
