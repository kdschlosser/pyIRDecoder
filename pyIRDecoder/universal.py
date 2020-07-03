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


from . import protocol_base
from . import utils


class Universal(protocol_base.IrProtocolBase):
    """
    IR decoder for unknown protocols.
    """

    def decode(self, data, frequency):

        norm_data = utils.clean_code(data[:], self.tolerance)
        norm_data = utils.build_mce_rlc(norm_data)

        for item in norm_data[:]:
            if norm_data.count(item) == 1:
                norm_data.remove(item)

        if norm_data[0] < 0:
            norm_data = norm_data[1:]

        if norm_data[-1] < 0:
            norm_data = norm_data[:-1]

        diff_time = 3

        last_pause = 0
        last_pulse = 0
        code = 0
        mask = 1
        for i, x in enumerate(norm_data):
            if i % 2:
                diff = max(diff_time, last_pause * 0.2)
                if -diff < x - last_pause < diff:
                    code |= mask
                last_pause = x
            else:
                diff = max(diff_time, last_pulse * 0.2)
                if -diff < x - last_pulse < diff:
                    code |= mask

                last_pulse = x
            mask <<= 1
        code |= mask

        params = {'CODE': code, 'frequency': frequency}

        code = protocol_base.IRCode(self, data, norm_data, params)

        return code

    def _test_decode(self):
        rlc = [[
            9024, -4512, 564, -1692, 564, -564, 564, -1692, 564, -564, 564, -564, 564, -564,
            564, -564, 564, -1692, 564, -564, 564, -564, 564, -564, 564, -564, 564, -1692,
            564, -1692, 564, -564, 564, -564, 564, -1692, 564, -1692, 564, -1692, 564, -564,
            564, -564, 564, -1692, 564, -1692, 564, -564, 564, -564, 564, -564, 564, -1692,
            564, -564, 564, -1692, 564, -564, 564, -564, 564, -1692, 564, -43992,
        ]]

        params = [dict(code=0x3755F777DDDFD7F54)]

        protocol_base.IrProtocolBase._test_decode(self, rlc, params)


Universal = Universal()
