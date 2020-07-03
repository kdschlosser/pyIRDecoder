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


from . import xml_handler
import os
import sys


class Config(object):
    _xml = None
    database_url = 'eventghost.net:43847'

    def __init__(self):
        if Config._xml is None:
            Config._xml = xml_handler.XMLRootElement('IRConfig')

        self.__xml = Config._xml

        if 'database_url' not in self:
            self.database_url = Config.database_url

        if 'Protocols' not in self:
            from . import protocol_base
            protocols = xml_handler.XMLElement('Protocols')
            base_path = os.path.dirname(__file__)
            base_mod_name = __name__.rsplit('.', 1)[0]
            for filename in os.listdir(base_path):
                if not filename.endswith('.py'):
                    continue

                def _skip_file():
                    for item in (
                        '__init__',
                        'protocol_base',
                        'pronto',
                        'config',
                        'xml_handler',
                        'code_wrapper'
                    ):
                        if filename.startswith(item):
                            return True
                    return False

                if _skip_file():
                    continue

                mod_name = '.' + os.path.splitext(filename)[0]
                __import__(mod_name)

                mod = sys.modules[base_mod_name + mod_name]
                for key, value in mod.__dict__.items():
                    if key.startswith('_'):
                        continue

                    if not isinstance(value, protocol_base.IrProtocolBase):
                        continue

                    tolerance = value.tolerance
                    frequency = value.frequency
                    bit_count = value.bit_count
                    encoding = value.encoding
                    irp = value.irp
                    parameters = value.encode_parameters

                    protocol = xml_handler.XMLElement(
                        'Protocol',
                        name=key,
                        tolerance=tolerance,
                        frequency=frequency,
                        bit_count=bit_count,
                        encoding=encoding
                    )

                    protocol.text = irp

                    for p_name, p_min, p_max in parameters:
                        parameter = xml_handler.XMLElement(
                            'Parameter',
                            name=p_name,
                            min=p_min,
                            max=p_max
                        )
                        protocol.ppend(parameter)

                    protocols.append(protocol)

                    break

            self.Protocols = protocols

        if 'LoadedProtocols' not in self:
            protocols = xml_handler.XMLElement('LoadedProtocols')

            for protocol in self.Protocols:
                protocol = xml_handler.XMLElement(
                    'Protocol',
                    name=protocol.name
                )

                protocols.append(protocol)

            self.LoadedProtocols = protocols

        if 'IRCodes' not in self:
            codes = xml_handler.XMLElement('IRCodes')
            self.IRCodes = codes

    def get_code_entry(self, code):
        for ir_code in self.IRCodes:
            if ir_code.rlc == code.normalized_rlc:
                return ir_code

    def get_code_name(self, code):
        if self.database_url:
            import requests
            try:
                response = requests.get(self.database_url)
                if response.status_code != 200:
                    raise requests.ConnectionError
            except requests.ConnectionError:
                pass
            else:
                token = response.content
                response = requests.get(self.database_url + '/' + token + '/get_name', params=dict(list(code)))
                if response.status_code == 200:
                    return response.content

    def __getitem__(self, item):
        return self.__xml[item]

    def __setitem__(self, key, value):
        self.__xml[key] = value

    def __getattr__(self, item):
        if item in self.__dict__:
            return self.__dict__[item]

        return getattr(self.__xml, item)

    def __setattr__(self, key, value):
        if '__xml' in key:
            object.__setattr__(self, key, value)
        else:
            setattr(self.__xml, key, value)

    def __len__(self):
        return len(self.__xml)

    def __iter__(self):
        return iter(self.__xml)

    def __delitem__(self, key):
        self.__xml.__delitem__(key)

    def __delattr__(self, item):
        self.__xml.__delattr__(item)

    def __contains__(self, item):
        from . import protocol_base

        if isinstance(item, protocol_base.IRCode):
            for ir_code in self.IRCodes:
                if ir_code.rlc == item.normalized_rlc:
                    return True

            return False

        return self.__xml.__contains__(item)

    def __str__(self):
        return str(self.__xml)

    def find_code_by_name(self, name):
        for ir_code in self.IRCodes:
            if ir_code.name == name:
                return ir_code

    def find_codes_by_protocol(self, protocol):
        res = []
        for ir_code in self.IRCodes:
            if ir_code.protocol == protocol:
                res += [ir_code]

        return res

    @classmethod
    def save(cls, path):
        if cls._xml is not None:
            path = os.path.expandvars(path)
            path = os.path.abspath(path)
            if 'database_url' not in cls._xml or cls.database_url != cls._xml.database_url:
                cls._xml.database_url = Config.database_url

            cls._xml.xml_file = path
            cls._xml.save()
            cls._xml.write_file()

    @classmethod
    def load(cls, path):
        path = os.path.expandvars(path)
        path = os.path.abspath(path)
        cls._xml = xml_handler.load(path, 'IRConfig')
