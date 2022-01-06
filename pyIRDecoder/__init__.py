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


from __future__ import print_function


class IRException(Exception):
    """IR error"""

    def __init__(self, *args):
        msg = ' '.join(str(arg) for arg in args)

        if not msg:
            self._msg = self.__doc__
        else:
            self._msg = msg

    def __str__(self):
        return self._msg


class TooManyBitsError(IRException):
    """Too many bits"""


class NotEnoughBitsError(IRException):
    """Not enough bits"""


class LeadInError(IRException):
    """Invalid lead in"""


class LeadOutError(IRException):
    """Invalid lead out"""


class EncodeError(IRException):
    """Encode error"""


class DecodeError(IRException):
    """Decode error"""


class IRStreamError(IRException):
    """Invalid IR stream"""


class RepeatTimeoutExpired(IRException):
    """Repeat timeout expired"""


class RepeatLeadInError(IRException):
    """Repeat lead in"""


class RepeatLeadOutError(IRException):
    """Repeat lead out"""


from .config import Config  # NOQA
from .pronto import pronto_to_rlc  # NOQA
from .utils import build_mce_rlc as _build_mce_rlc  # NOQA
from . import protocols  # NOQA


def rlc_to_mce(code):
    if isinstance(code[0], list):
        for i, rlc in enumerate(code):
            if rlc:
                rlc = _build_mce_rlc(rlc)
            code[i] = rlc
    else:
        code = _build_mce_rlc(code)

    return code


def pronto_to_mce(pronto_code):
    frequency, code = pronto_to_rlc(pronto_code)
    code = rlc_to_mce(code)
    return code, frequency


def decode_pronto_code(pronto_code):
    frequency, rlc = pronto.pronto_to_rlc(pronto_code)
    code = protocols.decode(rlc, frequency)

    if code.decoder == protocols.Universal:
        protocols.RC57F.enabled = False
        code = protocols.decode(rlc, frequency)

    if code.decoder == protocols.Universal:
        protocols.RC57F57.enabled = False
        code = protocols.decode(rlc, frequency)

    if code.decoder == protocols.Universal:
        protocols.Thomson.enabled = False
        code = protocols.decode(rlc, frequency)

    if code.decoder == protocols.Universal:
        protocols.NEC.enabled = False
        protocols.NECf16.enabled = False
        code = protocols.decode(rlc, frequency)

    return code


__all__ = (
    'protocols',
    'Config',
    'decode_pronto_code',
    'IRException',
    'DecodeError',
    'RepeatTimeoutExpired',
    'RepeatLeadInError',
    'RepeatLeadOutError',
    'pronto_to_rlc',
    'pronto_to_mce',
    'rlc_to_mce'
)


def main():
    import os
    import sys

    path = os.path.dirname(__file__)

    from . import protocol_base

    count = 0
    failed = []

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
            __import__('pyIRDecoder.' + mod_name)
        except:  # NOQA
            continue

        mod = sys.modules['pyIRDecoder.' + mod_name]

        for key, val in mod.__dict__.items():
            if key.startswith('_'):
                continue

            try:
                if isinstance(val, protocol_base.IrProtocolBase):
                    count += 1
                    try:
                        # noinspection PyProtectedMember
                        val._test_decode()
                    except:  # NOQA
                        failed += [mod_name]
                        import traceback
                        traceback.print_exc()
                    break

            except TypeError:
                pass

    print('number of decoders:', count)
    print('number of failed decodes:', failed)
