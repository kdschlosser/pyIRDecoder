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
    LeadInError,
    RepeatLeadOutError,
    EncodeError
)

TIMING = 444


class RC6MBIT(protocol_base.IrProtocolBase):
    """
    IR decoder for the RC6MBIT protocol.
    """
    irp = (
        '{36k,444,msb}<-1,1|1,-1>'
        '(6,-2,1:1,M:3,<-2,2|2,-2>(1-(T:1)),CODE:??,??)*'
    )
    frequency = 36000
    bit_count = 64
    encoding = 'msb'

    _lead_in = [TIMING * 6, -TIMING * 2]
    _lead_out = [-999999999999]
    _middle_timings = [{
        'start': 4,
        'stop': 5,
        'bursts': [[-TIMING * 2, TIMING * 2], [TIMING * 2, -TIMING * 2]]
    }]
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
        ['code', 0, 576460752303423487]
    ]

    def decode(self, data: list, frequency: int = 0) -> protocol_base.IRCode:
        code = data[:]
        normalized_code = []
        decoded = []

        mark, space = code[:2]
        code = code[2:]

        if not self._match(mark, self._lead_in[0]):
            raise LeadInError

        if not self._match(space, self._lead_in[1]):
            for burst, _ in self._bursts:
                if self._match(space - burst, self._lead_in[1]):
                    code.insert(0, burst)
                    break
            else:
                raise LeadInError

        normalized_code.extend(self._lead_in[:])

        pairs = []

        while code:
            try:
                timing1, timing2 = code[:2]
            except ValueError:
                break

            for burst1, burst2 in self._bursts:
                if not self._match(timing1, burst1):
                    continue

                if self._match(timing2, burst2):
                    pairs.append([burst1, burst2])
                    normalized_code.extend(pairs[-1][:])
                    code = code[2:]
                    break

                for half_bit, _ in self._bursts:
                    if half_bit > 0 < burst2 or half_bit < 0 > burst2:
                        if self._match(timing2, half_bit + burst2):
                            pairs.append([burst1, burst2])
                            normalized_code.extend(pairs[-1][:])
                            code = code[2:]
                            code.insert(0, half_bit)
                            break
                        if self._match(timing2, half_bit * 2 + burst2):
                            pairs.append([burst1, burst2])
                            normalized_code.extend(pairs[-1][:])
                            code = code[2:]
                            code.insert(0, half_bit * 2)
                            break
                else:
                    if len(code) == 2:
                        pairs.append([burst1, burst2])
                        normalized_code.extend(pairs[-1][:])
                        code = code[2:]
                    else:
                        raise DecodeError
                break
            else:
                for burst1, burst2 in self._bursts:
                    if self._match(timing1, burst1 * 2):
                        if self._match(timing2, burst2 * 2):
                            pairs.append([burst1 * 2, burst2 * 2])
                            normalized_code.extend(pairs[-1][:])
                            code = code[2:]
                            break
                        if self._match(timing2, burst2 * 3):
                            pairs.append([burst1 * 2, burst2 * 2])
                            normalized_code.extend(pairs[-1][:])
                            code = code[2:]
                            code.insert(0, burst2)
                            break
                else:
                    raise DecodeError

        for pair in pairs:
            if pair in self._bursts:
                decoded.append(self._bursts.index(pair))
            else:
                for i, (timing1, timing2) in enumerate(self._bursts):
                    if [timing1 * 2, timing2 * 2] == pair:
                        decoded.append(i)
                        break
                else:
                    raise DecodeError

        params = dict(frequency=self.frequency)

        for key, start_bit, stop_bit in self._parameters[:-1]:
            value = 0
            for i in range(start_bit, stop_bit + 1):
                value |= decoded[i] << (~i + stop_bit + 1)

            params[key] = protocol_base.IntegerWrapper(
                value,
                stop_bit + 1 - start_bit,
                self._bursts,
                self.encoding
            )

        decoded = decoded[5:]
        value = 0

        for i in range(len(decoded)):
            value |= decoded[i] << (~i + len(decoded))

        params['CODE'] = protocol_base.IntegerWrapper(
            value,
            len(decoded),
            self._bursts,
            self.encoding
        )

        normalized_rlc = []
        for pulse in normalized_code:
            if (
                len(normalized_rlc) and
                (
                    normalized_rlc[-1] < 0 > pulse or
                    normalized_rlc[-1] > 0 < pulse
                )
            ):
                normalized_rlc[-1] += pulse
                continue

            normalized_rlc += [pulse]

        total = sum(abs(item) for item in data)

        tt = sum(abs(item) for item in normalized_rlc)
        lead_out = tt - total
        if normalized_rlc[-1] < 0:
            normalized_rlc[-1] += lead_out
        else:
            normalized_rlc.append(lead_out)

        code = protocol_base.IRCode(
            self,
            data[:],
            normalized_rlc,
            params
        )

        if code.c0 != 1:
            raise DecodeError('Checksum failed')

        hex_code = hex(int(code.code))[2:].upper()
        hex_code = hex_code.zfill(len(hex_code) + (len(hex_code) % 2))
        code.name = (
            'RC6-' +
            str(code.mode) + '-' +
            str(len(decoded) + 5) + '.0' +
            str(code.mode) + ':' +
            hex_code
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
        mode: int,
        code: int,
        repeat_count: int = 0
    ) -> protocol_base.IRCode:
        c0 = protocol_base.IntegerWrapper(
            1,
            1,
            self._bursts,
            self.encoding
        )
        mode = protocol_base.IntegerWrapper(
            mode,
            3,
            self._bursts,
            self.encoding
        )
        code = protocol_base.IntegerWrapper(
            code,
            timings=self._bursts,
            encoding=self.encoding
        )

        if code.num_bits + 5 > self.bit_count:
            raise EncodeError('code is to large')

        packet = self._build_packet(
            c0.timings,
            mode.timings,
            [-TIMING * 2, TIMING * 2],
            code.timings
        )

        if packet[-1] == self._lead_out[0]:
            packet = packet[:-1]
        else:
            packet[-1] -= self._lead_out[0]

        tt = sum(abs(item) for item in packet)

        space = tt - 107000
        if packet[-1] < 0:
            packet[-1] += space
        else:
            packet += [space]

        lead_out = self._build_packet(
            c0.timings,
            mode.timings,
            [TIMING * 2, -TIMING * 2],
            code.timings
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

        # noinspection PyTypeChecker
        hex_code = hex(int(code))[2:].upper()
        hex_code = hex_code.zfill(len(hex_code) + (len(hex_code) % 2))

        params = dict(
            frequency=self.frequency,
            M=mode,
            CODE=code
        )

        ir_code = protocol_base.IRCode(
            self,
            (packet[:] * (repeat_count + 1)) + lead_out[:],
            ([packet[:]] * (repeat_count + 1)) + [lead_out[:]],
            params,
            repeat_count
        )

        ir_code.name = (
            'RC6-' +
            str(ir_code.mode) + '-' +
            str(code.num_bits + 5) + '.0' +
            str(ir_code.mode) + ':' + hex_code
        )

        return ir_code
