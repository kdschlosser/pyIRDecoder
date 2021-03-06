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


from __future__ import print_function


class IRException(Exception):
    pass


class EncodeError(IRException):
    pass


class DecodeError(IRException):
    pass


class RepeatTimeoutExpired(IRException):
    pass


class RepeatLeadIn(IRException):
    pass


class RepeatLeadOut(IRException):
    pass


from .ir_decoder import IRDecoder  # NOQA
from .ir_encoder import IREncoder  # NOQA
from .config import Config  # NOQA
from .pronto import pronto_to_rlc  # NOQA


def decode_pronto_code(pronto_code):
    decoder = IRDecoder()
    frequency, rlc = pronto.pronto_to_rlc(pronto_code)
    code = decoder.decode(rlc, frequency)

    if code.decoder == ir_decoder.Universal:
        decoder.RC57F.enabled = False
        code = decoder.decode(rlc, frequency)

    if code.decoder == ir_decoder.Universal:
        decoder.RC57F57.enabled = False
        code = decoder.decode(rlc, frequency)

    if code.decoder == ir_decoder.Universal:
        decoder.Thomson.enabled = False
        code = decoder.decode(rlc, frequency)

    if code.decoder == ir_decoder.Universal:
        decoder.NEC.enabled = False
        decoder.NECf16.enabled = False
        code = decoder.decode(rlc, frequency)

    return code


__all__ = (
    'IREncoder',
    'IREncoder',
    'Config',
    'decode_pronto_code',
    'IRException',
    'DecodeError',
    'RepeatTimeoutExpired',
    'RepeatLeadIn',
    'RepeatLeadOut',
    'pronto_to_rlc'
)

if __name__ == '__main__':
    import os
    import sys

    path = os.path.dirname(__file__)

    from . import protocol_base

    count = 0

    for f in os.listdir(path):
        if not f.endswith('py'):
            continue

        if f in (
            '__init__.py',
            'code_wrapper.py',
            'protocol_base.py',
            'utils.py',
            'xml_handler.py',
            'config.py',
        ):
            continue

        mod_name = f.rsplit('.', 1)[0]

        try:
            __import__('decoders.' + mod_name)
        except AttributeError:
            continue

        mod = sys.modules['decoders.' + mod_name]

        for key, val in mod.__dict__.items():
            if key.startswith('_'):
                continue

            try:
                if isinstance(val, protocol_base.IrProtocolBase):
                    val._test_decode()
                    count += 1

                    break
            except TypeError:
                continue

    print('number of decoders:', count)
