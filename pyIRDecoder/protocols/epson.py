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
from . import (
    DecodeError, 
    RepeatLeadInError,
    LeadInError,
    LeadOutError,
    TooManyBitsError,
    NotEnoughBitsError
)
    

TIMING = 577


class Epson(protocol_base.IrProtocolBase):
    """
    IR decoder for the Epson protocol.
    """

    irp = (
        '{38.4k,577,msb}<2,-1|1,-2|1,-1|2,-2>'
        '((4,-1,D:8,T1:2,OBC:6,T2:2,S:8,1,-75m)*,'
        '(4,-1,D:8,~F1:2,OBC:6,~F2:2,S:8,1,-250m))'
    )
    frequency = 38400
    bit_count = 26
    encoding = 'msb'
    _enabled = False

    _lead_in = [TIMING * 4, -TIMING]
    _lead_out = [TIMING, -250000]
    _repeat_lead_in = [TIMING * 4, -TIMING]
    _repeat_lead_out = [TIMING, -75000]
    _middle_timings = [[TIMING, -75000], TIMING * 4, -TIMING]
    _bursts = [
        [TIMING * 2, -TIMING],
        [TIMING, (-TIMING * 2)],
        [TIMING, -TIMING],
        [TIMING * 2, (-TIMING * 2)]
    ]

    _code_order = [
        ['D', 8],
        ['TOGGLE1', 2],
        ['OBC', 6],
        ['TOGGLE2', 2],
        ['S', 8],
        ['FUNCTION1', 2],
        ['FUNCTION2', 2]
    ]

    _parameters = [
        ['D', 0, 7],
        ['TOGGLE1', 8, 9],
        ['OBC', 10, 15],
        ['TOGGLE2', 16, 17],
        ['S', 18, 25],
        ['CD', 26, 33],
        ['FUNCTION1', 34, 35],
        ['COBC', 36, 41],
        ['FUNCTION2', 42, 43],
        ['CS', 44, 51],
    ]

    # [F:0..255]
    encode_parameters = [
        ['device', 0, 255],
        ['sub_device', 0, 255],
        ['obc', 0, 63],
        ['toggle1', 0, 3],
        ['toggle2', 0, 3],
        ['function1', 0, 3],
        ['function2', 0, 3]
    ]
    _partial_code = None

    # noinspection PyProtectedMember
    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        cleaned_code = []
        original_code = data[:]
        code = data[:]
        cleaned_second_code = None
        second_code = None

        try:
            mark, space = code[:2]
            code = code[2:]
        except ValueError:
            raise LeadInError

        if (
            self._match(mark, self._lead_in[0]) and
            self._match(space, self._lead_in[1])
        ):
            cleaned_code += self._lead_in[:]
        else:
            raise LeadInError

        try:
            mark, space = code[-2:]
            code = code[:-2]
        except ValueError:
            raise LeadOutError

        if (
            self._match(mark, self._lead_out[0]) and
            self._match(space, self._lead_out[1])
        ):
            for i in range(len(code), 2):
                e_mark, e_space = self._middle_timings[0]
                if (
                    self._match(code[i], e_mark) and
                    self._match(code[i + 1], e_space)
                ):
                    second_code = code[i + 1:]
                    cleaned_second_code = self._lead_in[:]
                    code = code[:i]
                    lead_out = self._middle_timings[0][:]
                    break
            else:
                lead_out = self._lead_out[:]
        elif (
            self._match(mark, self._middle_timings[0][0]) and
            self._match(space, self._middle_timings[0][1])
        ):
            lead_out = self._middle_timings[:]
        else:
            raise LeadOutError

        code_bits = []
        second_code_bits = []

        for i in range(0, len(code), 2):
            for j, (e_mark, e_space) in enumerate(self._bursts):
                if (
                    self._match(code[i], e_mark) and
                    self._match(code[i + 1], e_space)
                ):
                    cleaned_code += [e_mark, e_space]
                    code_bits.extend([j >> 1 & 1, j & 1])

                if (
                    second_code is not None and
                    (
                        self._match(second_code[i], e_mark) and
                        self._match(second_code[i + 1], e_space)
                    )
                ):
                    second_code.extend([j >> 1 & 1, j & 1])
                    cleaned_second_code += [e_mark, e_space]

        if len(code_bits) > self.bit_count:
            raise TooManyBitsError
        if len(code_bits) < self.bit_count:
            raise NotEnoughBitsError

        if second_code is not None:
            if len(second_code_bits) > self.bit_count:
                raise TooManyBitsError
            if len(second_code_bits) < self.bit_count:
                raise NotEnoughBitsError

            cleaned_second_code += self._lead_out[:]

        cleaned_code += lead_out

        params = dict(frequency=self.frequency)
        second_params = dict(frequency=self.frequency)

        if lead_out == self._lead_out:
            for key, start_bit, stop_bit in self._parameters[5:]:
                value = 0
                for i in range(start_bit, stop_bit + 1):
                    value |= code_bits[i - self.bit_count] << ~i + stop_bit + 1
                    
                params[key] = protocol_base.IntegerWrapper(
                    value,
                    stop_bit + 1 - start_bit,
                    self._bursts,
                    self.encoding
                )
        else:
            for key, start_bit, stop_bit in self._parameters[:5]:
                value = 0
                for i in range(start_bit, stop_bit + 1):
                    value |= code_bits[i] << ~i + stop_bit + 1

                params[key] = protocol_base.IntegerWrapper(
                    value,
                    stop_bit + 1 - start_bit,
                    self._bursts,
                    self.encoding
                )
            
            if second_code is not None:
                for key, start_bit, stop_bit in self._parameters[5:]:
                    value = 0
                    for i in range(start_bit, stop_bit + 1):
                        value |= (
                            second_code_bits[i - self.bit_count] <<
                            ~i + stop_bit + 1
                        )
                    second_params[key] = protocol_base.IntegerWrapper(
                        value,
                        stop_bit + 1 - start_bit,
                        self._bursts,
                        self.encoding
                    )

        code = protocol_base.IRCode(
            self,
            original_code[:len(code) + 4],
            cleaned_code,
            params
        )

        if second_code is not None:
            self._partial_code = None

            # noinspection PyUnresolvedReferences
            second_params['FUNCTION1'] = second_params['FUNCTION1'][True:2:0]
            # noinspection PyUnresolvedReferences
            second_params['FUNCTION2'] = second_params['FUNCTION2'][True:2:0]
            
            second_code = protocol_base.IRCode(
                self,
                original_code[len(second_code) + 4:],
                cleaned_second_code,
                second_params
            )
            
            if (
                code.device != second_code.cd or
                code.OBC != second_code.cobc or
                code.subdevice != second_code.cs
            ):
                raise DecodeError('Checksum mismatch')

            params.update(second_code._data)
            normalized_rlc = code._normalized_rlc
            normalized_rlc += second_code._normalized_rlc
            original_rlc = code._original_rlc
            original_rlc += second_code._original_rlc
            code = protocol_base.IRCode(
                self,
                original_rlc,
                normalized_rlc,
                params
            )

        elif 'FUNCTION1' in params:
            code._data['FUNCTION1'] = code._data['FUNCTION1'][True:2:0]
            code._data['FUNCTION2'] = code._data['FUNCTION2'][True:2:0]

            if self._partial_code is not None:
                if (
                    code.CD != self._partial_code.device or
                    code.COBC != self._partial_code.OBC or
                    code.CS != self._partial_code.sub_device

                ):
                    raise DecodeError('Checksum mismatch')

                last_code = self._partial_code
                params.update(last_code._data)
                normalized_rlc = last_code._normalized_rlc
                normalized_rlc += code._normalized_rlc
                original_rlc = last_code._original_rlc
                original_rlc += code._original_rlc
                code = protocol_base.IRCode(
                    self,
                    original_rlc,
                    normalized_rlc,
                    params
                )
                self._partial_code = None

        else:
            self._partial_code = code
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
        obc: int,
        toggle1: int,
        toggle2: int,
        function1: int,
        function2: int,
        repeat_count: int = 0
    ) -> protocol_base.IRCode:
        function1 = protocol_base.IntegerWrapper(
            function1,
            2,
            self._bursts,
            self.encoding
        )
        
        function2 = protocol_base.IntegerWrapper(
            function2,
            2,
            self._bursts,
            self.encoding
        )
        
        packet = self._build_packet(
            CD=device,
            FUNCTION1=function1[True:2:0],
            COBC=obc,
            FUNCTION2=function2[True:2:0],
            CS=sub_device
        )

        lead_out = self._lead_out[:]
        self._lead_out = self._middle_timings[0][:]
        
        repeat = self._build_packet(
            D=device,
            TOGGLE1=toggle1,
            OBC=obc,
            TOGGLE2=toggle2,
            S=sub_device
        )
        
        self._lead_out = lead_out[:]

        params = dict(
            frequency=self.frequency,
            D=device,
            TOGGLE1=toggle1,
            OBC=obc,
            TOGGLE2=toggle2,
            S=sub_device,
            FUNCTION1=function1,
            FUNCTION2=function2
        )

        code = protocol_base.IRCode(
            self,
            repeat + packet + (repeat * repeat_count),
            [repeat] + [packet] + ([repeat] * repeat_count),
            params,
            repeat_count
        )
        return code
