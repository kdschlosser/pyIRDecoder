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

import threading
from . import pronto
from . import utils
from . import xml_handler


class Timer(object):
    def __init__(self, func, duration):
        self.func = func
        self.duration = duration
        self.event = threading.Event()
        self.thread = None

    def cancel(self):
        if self.thread is not None:
            self.event.set()
            self.thread.join()

    def stop(self):
        if self.thread is not None:
            self.event.set()
            self.thread.join()

        self.func()

    def start(self):
        self.cancel()
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.thread.start()

    def run(self):
        self.event.wait(self.duration / 1000000.0)
        if not self.event.is_set():
            self.func()

        self.event.clear()
        self.thread = None

    @property
    def is_running(self):
        return self.thread is not None


class IRCode(object):

    def __init__(self, decoder, original_rlc, normalized_rlc, data):
        if not isinstance(original_rlc[0], list):
            original_rlc = [original_rlc]

        if not isinstance(normalized_rlc[0], list):
            normalized_rlc = [normalized_rlc]

        if decoder.repeat_timeout == 0:
            tt = sum(abs(item) for item in original_rlc)
            self._repeat_timer = Timer(self.__repeat_reset, tt + 10)
        else:
            self._repeat_timer = Timer(self.__repeat_reset, decoder.repeat_timeout)

        self._decoder = decoder
        self._original_rlc = original_rlc
        self._normalized_rlc = normalized_rlc
        self._data = data
        self._code = None
        self._name = None
        self._name = str(self)
        self._xml = None
        self.__repeat_callback = None

    def __repeat_reset(self):
        self.decoder.reset()
        if self.__repeat_callback is not None:
            self.__repeat_callback(self)

    @property
    def key_released_callback(self):
        return self.__repeat_callback

    @key_released_callback.setter
    def key_released_callback(self, value):
        self.__repeat_callback = value

    def save(self):
        if self not in self.decoder._saved_codes:
            self.decoder._saved_codes.append(self)

    def remove(self):
        if self in self.decoder._saved_codes:
            self.decoder._saved_codes.remove(self)

    @staticmethod
    def load_from_xml(xml, decoder):
        """
        :param xml:
        :type xml: xml_handler.XMLElement
        :return:
        """

        params = {k.upper(): v for k, v in xml.attrib.items()}

        name = params.pop('NAME')
        params['frequency'] = params.pop('FREQUENCY')
        original_rlc = list(int(item) for item in xml.OriginalRLC.text.split(', '))
        normalized_rlc = list(int(item) for item in xml.NormalizedRLC.text.split(', '))

        self = IRCode(decoder, original_rlc, normalized_rlc, params)
        self.name = name
        self._xml = xml
        return self

    @property
    def xml(self):
        if self._xml is None:
            self._xml = xml_handler.XMLElement(
                'IRCode',
                decoder=self.decoder.name,
                **self._data
            )
            xml = xml_handler.XMLElement('OriginalRLC')
            text = []

            for item in self._original_rlc:
                if item > 0:
                    text += ['+' + str(item)]
                else:
                    text += [str(item)]

            xml.text = ', '.join(text)

            self._xml.OriginalRLC = xml

            xml = xml_handler.XMLElement('NormalizedRLC')
            text = []

            for item in self._normalized_rlc:
                if item > 0:
                    text += ['+' + str(item)]
                else:
                    text += [str(item)]

            xml.text = ', '.join(text)

            self._xml.NormalizedRLC = xml

        self._xml.name = self.name

        return self._xml

    @property
    def repeat_timer(self):
        return self._repeat_timer

    @property
    def params(self):
        res = []

        for key in (
            'mode',
            'n',
            'h',
            'oem1',
            'oem2',
            'device',
            'sub_device',
            'extended_function',
            'function',
            'g',
            'x',
            'code'
        ):
            try:
                if getattr(self, key) is not None:
                    res += [key]
            except AttributeError:
                continue

        for key in sorted(list(self._data.keys())):
            for char in list('MDFSECTXOHGN'):
                if key.upper().startswith(char):
                    break
            else:
                res += [key.lower()]

        if 'T' in self._data:
            res += ['toggle']

        return res

    @property
    def decoder(self):
        return self._decoder

    @property
    def frequency(self):
        return self._data['frequency']

    @property
    def original_rlc(self):
        return self._original_rlc[:]

    @property
    def normalized_rlc(self):
        return self._normalized_rlc[:]

    @property
    def original_rlc_pronto(self):
        res = []
        for code in self._original_rlc:
            code = [abs(item) for item in code]
            res += [pronto.rlc_to_pronto(self.frequency, code)]

        return res

    @property
    def normalized_rlc_pronto(self):
        res = []
        for code in self._normalized_rlc:
            code = [abs(item) for item in code]
            res += [pronto.rlc_to_pronto(self.frequency, code)]

        return res

    @property
    def original_mce_rlc(self):
        res = []
        for code in self._original_rlc:
            res += [utils.build_mce_rlc(code[:])]

        return res

    @property
    def original_mce_pronto(self):
        res = []
        for code in self.original_mce_rlc:
            code = [abs(item) for item in code]
            res += [pronto.rlc_to_pronto(self.frequency, code)]

        return res

    @property
    def normalized_mce_rlc(self):
        res = []
        for code in self._normalized_rlc:
            code = [abs(item) for item in code]
            res += [pronto.rlc_to_pronto(self.frequency, code)]

        return res

    @property
    def normalized_mce_pronto(self):
        res = []
        for code in self.normalized_mce_rlc:
            code = [abs(item) for item in code]
            res += [pronto.rlc_to_pronto(self.frequency, code)]

        return res

    @property
    def device(self):
        return self._data.get('D', None)

    @property
    def sub_device(self):
        return self._data.get('S', None)

    @property
    def function(self):
        return self._data.get('F', None)

    @property
    def toggle(self):
        return self._data.get('T', None)

    @property
    def mode(self):
        return self._data.get('M', None)

    @property
    def n(self):
        return self._data.get('N', None)

    @property
    def g(self):
        return self._data.get('G', None)

    @property
    def x(self):
        return self._data.get('X', None)

    @property
    def extended_function(self):
        return self._data.get('E', None)

    @property
    def checksum(self):
        return self._data.get('CHECKSUM', None)

    @property
    def u(self):
        return self._data.get('U', None)

    @property
    def oem1(self):
        return self._data.get('OEM1', None)

    @property
    def oem2(self):
        return self._data.get('OEM2', None)

    def __getattr__(self, item):
        if item in self.__dict__:
            return self.__dict__[item]

        if item.upper() in self._data:
            return self._data[item.upper()]

        raise AttributeError(item)

    def __int__(self):
        bits = ''

        def _get_bits(val, strt, stp):
            bts = []

            for i in range(strt, stp + 1):
                bts.insert(0, str(self._decoder._get_bit(val, i)))

            return ''.join(bts)

        if 'CODE' in self._data:
            bits += bin(self.code)[2:]

        else:
            for name, start, stop in self._decoder._parameters:
                if name.startswith('C'):
                    continue

                if len(name) == 2:
                    name = name[:1]

                if name in self._data:
                    bits += _get_bits(self._data[name], start, stop)

        return int(bits, 2)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def hexdecimal(self):
        res = hex(int(self))[2:].upper().rstrip('L')
        return '0x' + res.zfill(len(res) + (len(res) % 2))

    def __eq__(self, other):
        if isinstance(other, list):
            if len(other) != len(self.original_rlc):
                return False

            for i in range(len(other)):
                if not self.decoder._match(other[i], self._normalized_rlc[i]):
                    return False

            return True

        if isinstance(other, IRCode):
            return (
                other.decoder == self.decoder and
                other._data == self._data
            )
        else:
            return other == self.normalized_pronto

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        if self._name is None:
            res = []
            for key in self.params:
                value = getattr(self, key)
                res += [('%X' % (value,)).zfill(2)]

            return self.decoder.name + '.' + ':'.join(res)

        return self._name
