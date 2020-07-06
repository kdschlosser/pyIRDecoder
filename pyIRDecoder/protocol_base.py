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
import math
import threading
from . import pronto
from . import utils
from . import xml_handler
from . import code_wrapper
from . import (
    DecodeError,
    RepeatLeadIn,
    RepeatLeadOut
)


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
        self.event.wait(self.duration)
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
            original_code = [original_rlc]

        if not isinstance(normalized_rlc[0], list):
            normalized_code = [normalized_rlc]

        self._repeat_timer = Timer(decoder.reset, decoder.repeat_timeout)
        self._decoder = decoder
        self._original_rlc = original_rlc
        self._normalized_rlc = normalized_rlc
        self._data = data
        self._code = None
        self.name = None
        self.name = str(self)
        self.__xml = None

    @property
    def xml(self):
        if self.__xml is None:
            self.__xml = xml_handler.XMLElement(
                'IRCode',
                decoder=self.decoder,
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

            self.__xml.OriginalRLC = xml

            xml = xml_handler.XMLElement('NormalizedRLC')
            text = []

            for item in self._normalized_rlc:
                if item > 0:
                    text += ['+' + str(item)]
                else:
                    text += [str(item)]

            xml.text = ', '.join(text)

            self.__xml.NormalizedRLC = xml

        return self.__xml

    @property
    def repeat_timer(self):
        return self._repeat_timer

    def __iter__(self):
        yield 'decoder', self.decoder.name
        for key, value in self._data.items():
            yield key, value

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

        def _get_num_bits(label):
            for name, start, stop in self._decoder._parameters:
                if name != label:
                    continue
                return (stop + 1) - start

            return 0

        def _get_bits(val, num_bits):
            bts = []

            for i in range(num_bits):
                bts.insert(0, str(self._decoder._get_bit(val, i)))

            return ''.join(bts)

        keys = []

        for key in (
            'M',
            'N',
            'H',
            'OEM1',
            'OEM2',
            'D',
            'S',
            'E',
            'F',
            'G',
            'X',
            'CODE'
        ):
            if key in self._data:
                if key == 'CODE':
                    bits += bin(self.code)[2:]
                else:
                    keys += [key]
                    bits += _get_bits(
                        getattr(self, key.lower()),
                        _get_num_bits(key)
                    )

        for key in sorted(list(self._data.keys())):
            if key in keys:
                continue

            for char in list('MDFSECTXOHNG'):
                if key.upper().startswith(char):
                    break
            else:
                keys += [key]
                bits += _get_bits(
                    getattr(self, key.lower()),
                    _get_num_bits(key)
                )

        return int(bits, 2)

    @property
    def hexdecimal(self):
        res = hex(int(self))[2:].upper().rstrip('L')
        return '0x' + res.zfill(len(res) + (len(res) % 2))

    def __eq__(self, other):
        if isinstance(other, list):
            return self.normalized_rlc == other

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
        if self.name is None:
            res = []
            for key in self.params:
                value = getattr(self, key)
                res += [('%X' % (value,)).zfill(2)]

            return self.decoder.name + '.' + ':'.join(res)

        return self.name


class IrProtocolBase(object):
    irp = ''
    frequency = 36000
    tolerance = 1
    frequency_tolerance = 2
    bit_count = 0
    encoding = ''

    _lead_in = []
    _lead_out = []
    _bursts = []

    _repeat_lead_in = []
    _repeat_lead_out = []
    _middle_timings = []
    _repeat_bursts = []

    _parameters = []
    encode_parameters = []
    repeat_timeout = 0

    def __init__(self):
        self._last_code = None
        self._enabled = True

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        self._enabled = value

    @property
    def name(self):
        return self.__class__.__name__

    def reset(self):
        pass

    def _test_decode(self, rlc=None, params=None):
        print(self.__class__.__name__, 'decode test.....')
        self.tolerance = 1
        if rlc is None:
            return

        code = None

        for i in range(len(rlc)):
            data = rlc[i]
            param = params[i]
            try:
                code = self.decode(data, self.frequency)
                print('decoded friendly', code)
                print('decoded hexdecimal', code.hexdecimal)

            except (RepeatLeadIn, RepeatLeadOut):
                continue

            else:
                for key, value in param.items():
                    if getattr(code, key) != value:
                        print(code)
                        print(i, key, value, getattr(code, key))
                        print(data)

                        code = code_wrapper.CodeWrapper(
                            self.encoding,
                            self._lead_in,
                            self._lead_out,
                            self._middle_timings,
                            self._bursts,
                            self.tolerance,
                            data[:]
                        )

                        print(code._stream_pairs)
                        raise RuntimeError

        return code

    def _test_encode(self, params=None):
        if params is None:
            return

        codes = self.encode(**params)
        found_code = None
        for code in codes:
            try:
                code = self.decode(code)
            except:
                continue

            if code is not None:
                found_code = code

        if found_code is None:
            raise AssertionError('encode failed.')

        for key, value in params.items():
            assert getattr(found_code, key) == value

    def encode(self, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def _reverse_bits(cls, value, num_bits):
        res = 0

        for i in range(num_bits):
            res = cls._set_bit(res, (~i + num_bits), cls._get_bit(value, i))

        return res

    @classmethod
    def _count_one_bits(cls, value):
        count = 0

        for i in range(64):
            count += int(cls._get_bit(value, i))

        return count

    @classmethod
    def _get_bits(cls, data, start_bit, stop_bit):
        res = 0
        for i in range(start_bit, stop_bit + 1):
            res = cls._set_bit(res, i - start_bit, cls._get_bit(data, i))

        return res

    def _build_packet(self, *data):
        data = list(data)

        if self.encoding == 'msb':
            for i, items in enumerate(data):
                if isinstance(items, list):
                    new_data = []
                    for item in items:
                        new_data.insert(0, item)

                    data[i] = new_data[:]

        def flatten_and_compress(lst):
            res = []
            for itm in lst:
                if isinstance(itm, int):
                    if res and (res[-1] > 0 < itm or res[-1] < 0 > itm):
                        res[-1] += itm
                    else:
                        res += [itm]
                else:
                    res += flatten_and_compress(itm)
                    res = flatten_and_compress(res)

            return res

        packet = []

        for item in data:
            if isinstance(item, tuple):
                packet += [item]
            else:
                packet += item

        packet = self._lead_in[:] + packet + self._lead_out[:]

        if self._lead_out and packet[-1] > 0:
            packet = flatten_and_compress(packet[:-1])
            tt = sum(abs(item) for item in packet)
            packet += [-(self._lead_out[-1] - tt)]

        packet = flatten_and_compress(packet)
        return packet[:]

    def decode(self, data, frequency=0):
        if frequency > 0:
            if not self._match(frequency, self.frequency, self.frequency_tolerance / 10.0):
                raise DecodeError('Incorrect frequency')

        code = code_wrapper.CodeWrapper(
            self.encoding,
            self._lead_in[:],
            self._lead_out[:],
            self._middle_timings[:],
            self._bursts[:],
            self.tolerance,
            data[:]
        )

        if code.num_bits > self.bit_count:
            raise DecodeError('To many bits')
        elif code.num_bits < self.bit_count:
            raise DecodeError('Not enough bits')

        params = dict(frequency=self.frequency)
        for name, start, stop in self._parameters:
            params[name] = code.get_value(start, stop)

        c = IRCode(self, code.original_code, list(code), params)
        c._code = code
        return c

    def _get_timing(self, num, index):
        return self._bursts[self._get_bit(num, index)]

    @staticmethod
    def _set_bit(value, bit_num, state):
        if state:
            return value | (1 << bit_num)
        else:
            return value & ~(1 << bit_num)

    @staticmethod
    def _get_bit(value, bit_num):
        return int(value & (1 << bit_num) > 0)

    @classmethod
    def _invert_bits(cls, n, num_bits):
        res = 0

        for i in range(num_bits):
            res = cls._set_bit(res, i, not cls._get_bit(n, i))

        return res

    def _match(self, value, expected_timing_value, tolerance=None):
        if tolerance is None:
            tolerance = self.tolerance

        high = math.floor(expected_timing_value + (expected_timing_value * (tolerance / 100.0)))
        low = math.floor(expected_timing_value - (expected_timing_value * (tolerance / 100.0)))

        # do a flip flop of the high and low so the same expression can
        # be used when evaluating a raw timing
        if expected_timing_value < 0:
            low, high = high, low

        return low <= value <= high



