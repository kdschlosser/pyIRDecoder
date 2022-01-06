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
import math
import six
from typing import Sequence, Optional

from . import code_wrapper
from . import xml_handler

from . import (
    DecodeError,
    RepeatLeadInError,
    RepeatLeadOutError,
    TooManyBitsError,
    NotEnoughBitsError,
    IRStreamError,
    IRException
)

from .config import Config
from .integer_wrapper import IntegerWrapper
from .ir_code import IRCode


class ProtocolBaseMeta(type):
    _classes = []

    def __init__(cls, name, bases, dct):
        super(ProtocolBaseMeta, cls).__init__(name, bases, dct)

        if cls not in ProtocolBaseMeta._classes:
            ProtocolBaseMeta._classes += [cls]

    def __call__(cls, parent=None, xml=None):
        if xml is not None and cls == IrProtocolBase:
            for protocol in ProtocolBaseMeta._classes:
                if protocol.__name__ == xml.name:
                    return protocol(parent, xml)

            raise RuntimeError('Unable to locate a protocol named ' + xml.name)

        return super(ProtocolBaseMeta, cls).__call__(parent, xml)


@six.add_metaclass(ProtocolBaseMeta)
class IrProtocolBase(object):
    irp = ''
    frequency = 36000

    bit_count = 0
    encoding = ''

    _lead_in = []
    _lead_out = []
    _bursts = []

    _repeat_lead_in = []
    _repeat_lead_out = []
    _middle_timings = []
    _repeat_bursts = []
    _has_repeat_lead_out = False

    _code_order = []
    _parameters = []
    encode_parameters = []
    repeat_timeout = 0

    _enabled = True

    def __init__(self, parent=None, xml=None):
        import threading
        self.__last_code = None
        self.__code_lock = threading.RLock()
        self._tolerance = 20
        self._frequency_tolerance = 2
        self._saved_codes = []
        self._sequence = []
        self._parent = parent

        self._lead_in = self._lead_in[:]
        self._lead_out = self._lead_out[:]
        self._bursts = self._bursts[:]
        self._repeat_lead_in = self._repeat_lead_in[:]
        self._repeat_lead_out = self._repeat_lead_out[:]
        self._middle_timings = self._middle_timings[:]
        self._repeat_bursts = self._repeat_bursts[:]

        self._parameters = self._parameters[:]
        self.encode_parameters = self.encode_parameters[:]
        self.repeat_timeout = self.repeat_timeout

        if self.repeat_timeout == 0:
            if self._repeat_lead_out and self._repeat_lead_out[-1] > 0:
                self.repeat_timeout = self._repeat_lead_out[-1]

            elif (
                not self._repeat_bursts and
                (self._repeat_lead_in or self._repeat_lead_out)
            ):
                tt = sum(
                    abs(item) for item in
                    self._repeat_lead_in[:] + self._repeat_lead_out[:]
                )
                self.repeat_timeout = tt

            elif self._lead_out and self._lead_out[-1] > 0:
                self.repeat_timeout = self._lead_out[-1]

        if xml is not None:
            self._enabled = xml.enabled
            self._tolerance = xml.tolerance
            self._frequency_tolerance = xml.frequency_tolerance

            for code in xml.Codes:
                code = IRCode.load_from_xml(code, self)
                code.save()

        self._xml = xml

    @property
    def has_repeat_lead_out(self) -> bool:
        return self._has_repeat_lead_out

    @property
    def config(self) -> Optional[Config]:
        if self._parent is not None:
            return self._parent.config

    @property
    def _last_code(self) -> Optional[IRCode]:
        with self.__code_lock:
            return self.__last_code

    @_last_code.setter
    def _last_code(self, value: Optional[IRCode]):
        with self.__code_lock:
            self.__last_code = value

    def __iter__(self):
        for code in self._saved_codes:
            yield code

    def frequency_match(self, frequency: int) -> bool:
        return self._match(
            frequency,
            self.frequency,
            self.frequency_tolerance
        )

    @property
    def xml(self) -> xml_handler.XMLElement:
        if self._xml is None:
            self._xml = xml_handler.XMLElement(
                'IRProtocol',
                name=self.name
            )

        self._xml.enabled = self._enabled
        self._xml.tolerance = self._tolerance
        self._xml.frequency_tolerance = self._frequency_tolerance

        for code_xml in self._xml:
            self._xml.remove(code_xml)

        for code in self._saved_codes:
            self._xml.append(code.xml)

        return self._xml

    @property
    def function(self) -> Sequence[int]:
        for name, min_val, max_val in self.encode_parameters:
            if name == 'function':
                return list(range(min_val, max_val + 1))

        return []

    @property
    def device(self) -> Sequence[int]:
        for name, min_val, max_val in self.encode_parameters:
            if name == 'device':
                return list(range(min_val, max_val + 1))

        return []

    @property
    def sub_device(self) -> Sequence[int]:
        for name, min_val, max_val in self.encode_parameters:
            if name == 'sub_device':
                return list(range(min_val, max_val + 1))

        return []

    @property
    def extended_function(self) -> Sequence[int]:
        for name, min_val, max_val in self.encode_parameters:
            if name == 'extended_function':
                return list(range(min_val, max_val + 1))

        return []

    @property
    def mode(self) -> Sequence[int]:
        for name, min_val, max_val in self.encode_parameters:
            if name == 'mode':
                return list(range(min_val, max_val + 1))

        return []

    @property
    def toggle(self) -> Sequence[int]:
        for name, min_val, max_val in self.encode_parameters:
            if name == 'toggle':
                return list(range(min_val, max_val + 1))

        return []

    @property
    def oem1(self) -> Sequence[int]:
        for name, min_val, max_val in self.encode_parameters:
            if name == 'oem1':
                return list(range(min_val, max_val + 1))

        return []

    @property
    def oem2(self) -> Sequence[int]:
        for name, min_val, max_val in self.encode_parameters:
            if name == 'oem2':
                return list(range(min_val, max_val + 1))

        return []

    def __call__(self, parent):
        cls = self.__class__(parent)
        return cls

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool):
        self._enabled = value

    @property
    def tolerance(self) -> float:
        return self._tolerance

    @tolerance.setter
    def tolerance(self, value: float):
        self._tolerance = value

    @property
    def frequency_tolerance(self) -> float:
        return self._frequency_tolerance

    @frequency_tolerance.setter
    def frequency_tolerance(self, value: float):
        self._frequency_tolerance = value

    @property
    def name(self) -> str:
        return self.__class__.__name__

    def reset(self, code: IRCode) -> None:
        if self._last_code is not None and self._last_code == code:
            self._last_code = None

    def encode(self, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def _build_packet(cls, *args, **kwargs):
        args = list(args)

        if cls._parameters:
            parameters = cls._parameters[:]
        else:
            try:
                parameters = cls._parameters2[:]
            except AttributeError:
                parameters = cls._parameters1[:]

        for key, start, stop in parameters:
            if key in kwargs:
                param = kwargs[key]
                if not isinstance(param, IntegerWrapper):
                    num_bits = stop + 1 - start

                    param = IntegerWrapper(
                        param,
                        num_bits,
                        cls._bursts,
                        cls.encoding
                    )

                args.append(param.timings)

        # if self.encoding == 'msb':
        #     for i, items in enumerate(data):
        #         if isinstance(items, list):
        #             new_data = []
        #             for item in items:
        #                 new_data.insert(0, item)
        #
        #             data[i] = new_data[:]

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

        packet = list(args)

        packet = cls._lead_in[:] + packet[:] + cls._lead_out[:]

        if cls._lead_out and packet[-1] > 0:
            packet = flatten_and_compress(packet[:-1])
            tt = sum(abs(item) for item in packet)
            packet += [tt - cls._lead_out[-1]]
        else:
            packet = flatten_and_compress(packet)

        return packet[:]

    def decode(self, data: list, frequency: int = 0) -> IRCode:
        with self.__code_lock:
            if self._last_code is not None and (
                self._repeat_lead_in or
                self._repeat_lead_out
            ):
                try:
                    code = code_wrapper.CodeWrapper(
                        self.encoding,
                        self._repeat_lead_in[:],
                        self._repeat_lead_out[:],
                        [],
                        self._repeat_bursts[:],
                        self.tolerance,
                        data[:]
                    )

                    if (
                        self._repeat_bursts and
                        self.__class__.decode == IrProtocolBase.decode
                    ):
                        params = dict(frequency=self.frequency)
                        for name, start, stop in self._parameters:
                            params[name] = code.get_value(start, stop)

                        c = IRCode(
                            self,
                            code.original_code,
                            list(code),
                            params
                        )
                        c._code = code

                        if c == self._last_code:
                            self._last_code._code = code
                            return self._last_code
                        else:
                            self._last_code.repeat_timer.stop()
                            raise DecodeError

                    self._last_code._code = code
                    return self._last_code

                except IRException:
                    pass

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
            raise TooManyBitsError(self.bit_count, ':', code.stream_pairs)
        elif code.num_bits < self.bit_count:
            raise NotEnoughBitsError(self.bit_count, ':', code.stream_pairs)

        params = dict(frequency=self.frequency)
        for name, start, stop in self._parameters:
            params[name] = code.get_value(start, stop)

        c = IRCode(self, code.original_code, list(code), params)
        c._code = code

        if self.__class__.decode == IrProtocolBase.decode:
            with self.__code_lock:
                if self._last_code is not None:
                    if self._last_code == c:
                        return self._last_code

                    self._last_code.repeat_timer.stop()

                self._last_code = c

        return c

    @classmethod
    def _build_repeat_packet(cls, repeat_count=0):
        timings = cls._repeat_lead_in[:] + cls._repeat_lead_out[:]
        if timings[-1] > 0:
            tt = sum(abs(item) for item in timings[:-1])
            timings[-1] = -(timings[-1] - tt)

        packet = [timings] * repeat_count
        return packet

    def _match(self, value, expected_timing_value, tolerance=None):
        if tolerance is None:
            tolerance = self.tolerance

        high = math.floor(
            expected_timing_value +
            (expected_timing_value * (tolerance / 100.0))
        )
        low = math.floor(
            expected_timing_value -
            (expected_timing_value * (tolerance / 100.0))
        )

        # do a flip flop of the high and low so the same expression can
        # be used when evaluating a raw timing
        if expected_timing_value < 0:
            low, high = high, low

        return low <= value <= high
