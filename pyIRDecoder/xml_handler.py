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

import threading
import os
from io import BytesIO, StringIO

ESCAPE_CHARS = (
    ('&', '&amp;'),
    ('<', '&lt;'),
    ('>', '&gt;'),
    ('"', '&quot;'),
    ("'", '&apos;')
)

UNESCAPE_CHARS = (
    ('&amp;', '&'),
    ('&lt;', '<'),
    ('&gt;', '>'),
    ('&quot;', '"'),
    ('&apos;', "'")
)


class XMLAttributes(object):

    def __init__(self, parent):
        self.__parent = parent
        self.__data = {}

    def __getitem__(self, key):
        if key in self.__data:
            value = self.__data[key]

            try:
                value = eval(value)
            except:  # NOQA
                pass

            try:
                return value.decode('utf-8')
            except:  # NOQA
                return value

        raise KeyError(key)

    def __str__(self):
        output = ''

        for key in sorted(list(self.keys())[:]):
            value = str(self.__data[key])

            for item in ESCAPE_CHARS:
                value = value.replace(*item)

            output += ' {0}="{1}"'.format(key, value)

        return output

    def __setitem__(self, key, value):
        if not key.replace('_', '').isalpha():
            raise KeyError(
                'special characters and spaces are not allowed in an '
                'XMLElements attribute name. {0}'.format(repr(key))
            )
        try:
            value = value.decode('utf-8')
        except UnicodeDecodeError:
            pass
        except:  # NOQA
            value = str(value)

        self.__data[key] = value
        self.__parent.save()

    def __delitem__(self, key):
        if key in self.__data:
            del self.__data[key]

            self.__parent.save()

    def __iter__(self):
        return iter(self.__data.keys())

    def keys(self):
        return self.__data.keys()

    def values(self):
        return self.__data.values()

    def pop(self, *args, **kwargs):
        res = self.__data.pop(*args, **kwargs)
        self.__parent.save()
        return res

    def __contains__(self, item):
        return self.__data.__contains__(item)


class XMLElement(object):

    def __init__(self, tag, **kwargs):
        self.__text = None
        self.__tag = tag
        self.__parent = None
        self.__attrib = XMLAttributes(self)
        self.__children = []

        for key, value in kwargs.items():
            self[key] = value

    def find_attribute(self, path):
        obj = self

        while path.startswith('.'):
            if obj.parent is None:
                path.letrip('.')
            else:
                obj = obj.parent
                path = path[1:]

        if path.endswith('.'):
            recursive = True
            path = path[:-1]
        else:
            recursive = False

        def iter_search(parent, res=()):
            if isinstance(res, tuple):
                res = list(res)
            for child in parent.sub_elements:
                if path in child.attrib:
                    res += [child]
                if recursive:
                    res = iter_search(child, res)

            return res

        return iter_search(obj)

    def find_tag(self, path):
        obj = self

        while path.startswith('.'):
            if obj.parent is None:
                path.letrip('.')
            else:
                obj = obj.parent
                path = path[1:]

        if path.endswith('.'):
            recursive = True
            path = path[:-1]
        else:
            recursive = False

        def iter_search(parent, res=()):
            if isinstance(res, tuple):
                res = list(res)
            for child in parent.sub_elements:
                if child.tag == path:
                    res += [child]
                if recursive:
                    res = iter_search(child, res)
            return res

        return iter_search(obj)

    @classmethod
    def from_string(cls, str_element):
        str_element = str_element.split('?>', 1)[-1].strip()

        while '<!--' in str_element:
            front = str_element.split('<!--', 1)[0]
            back = str_element.split('-->', 1)[-1]

            str_element = front + back.lstrip()

        elements = list(
            item.strip() for item in str_element.strip().split('<')
            if item.strip()
        )

        attr_line = elements.pop(0)

        attr_line = attr_line.split('>')

        if len(attr_line) == 2:
            attr_line, text = attr_line
        else:
            attr_line = attr_line[0]
            text = ''

        attr_line = attr_line.split(' ', 1)

        if len(attr_line) == 2:
            tag, attr_line = attr_line
        else:
            tag = attr_line[0]
            attr_line = ''

        if tag.endswith('/') or attr_line.endswith('/'):
            sub_nodes = []
        else:
            sub_nodes = elements[:-1]

        tag = tag.rstrip('/').strip()
        attr_line = attr_line.rstrip('/').strip()
        text = text.strip()

        self = cls(tag)

        quote_count = None

        key = ''
        value = ''

        for char in list(attr_line):
            if quote_count is None and char in (' ', '\n', '\t'):
                continue

            if quote_count is None and char == '=':
                quote_count = 0
                continue

            if char in ('"', "'"):
                if quote_count == 0:
                    quote_count = 1
                    continue
                else:
                    quote_count = None

                    for item in UNESCAPE_CHARS:
                        value = value.replace(*item)

                    self[key.strip()] = value
                    key = ''
                    value = ''
                    continue

            if quote_count == 1:
                value += char
            else:
                key += char

        if key and value:
            self[key.strip()] = value

        if text:
            for item in UNESCAPE_CHARS:
                text = text.replace(*item)

            num_indents = 0

            for line in text.splitlines():
                indent_count = line.count('    ')

                for i in range(indent_count, -1, -1):
                    if line.startswith('    ' * indent_count):
                        num_indents = i
                        break

            self.text = text.replace('    ' * num_indents, '').strip('\n')

        while sub_nodes:
            sub_element = sub_nodes.pop(0)
            if sub_element.endswith('/>'):
                self.append(XMLElement.from_string('<' + sub_element))
                continue

            sub_tag = sub_element.split(' ', 1)[0]
            sub_tag = sub_tag.split('>')[0].strip()

            while (
                not '/' + sub_tag + '>' in sub_element and
                not '/' + sub_tag + ' >' in sub_element
            ):
                sub_element += '<' + sub_nodes.pop(0)

            self.append(XMLElement.from_string('<' + sub_element))

        return self

    def clear(self):
        for child in self.__children:
            child.parent = None

        del self.__children[:]

    @property
    def attrib(self):
        return self.__attrib

    @property
    def sub_elements(self):
        return self.__children

    def __iter__(self):
        for child in self.__children:
            yield child

    def __len__(self):
        return len(self.__children)

    @property
    def tag(self):
        return self.__tag

    @tag.setter
    def tag(self, value):
        old_name = self.__tag

        try:
            tag = value.decode('utf-8')
        except AttributeError:
            tag = value

        if (
            old_name in self.__parent and
            getattr(old_name, self.__tag) == self
        ):
            if tag in self.__parent:
                raise RuntimeError(
                    'new tag name already exists '
                    'in parent element ("{0}")'.format(tag)
                )

            delattr(self.__parent, old_name)
            self.__tag = tag
            setattr(self._parent, tag, self)
        else:
            self.__tag = tag

    @property
    def text(self):
        try:
            return self.__text.decode('utf-8')
        except:  # NOQA
            return self.__text

    @text.setter
    def text(self, value):
        if value is None:
            self.__text = None
            return

        try:
            text = value.encode('utf-8')
        except UnicodeDecodeError:
            text = value

        self.__text = text

    def __str__(self):
        output = '<' + self.tag
        output += str(self.__attrib)

        if self.__text is None and not self.__children:
            output += '/>\n'
            return output

        output += '>\n'

        if self.__text is not None:
            text = self.text

            for item in UNESCAPE_CHARS:
                text = text.replace(*item)

            for item in ESCAPE_CHARS:
                text = text.replace(*item)

            if (
                len(output + text) < 180 and
                '\n' not in text and
                not self.__children
            ):
                output = output[:-1] + text
                output += '</{0}>\n'.format(self.__tag)
                return output

            else:
                text = list(
                    '    ' + line for line in text.splitlines()
                )
                output += ''.join(text) + '\n'

        if self.__children:
            for child in self.__children:
                child = str(child)
                child = '\n'.join('    ' + line for line in child.splitlines())
                output += child + '\n'
        output += '</{0}>\n'.format(self.__tag)
        return output

    @property
    def parent(self):
        return self.__parent

    @parent.setter
    def parent(self, new_parent):
        if new_parent is None:
            if (
                self.__parent is not None and
                self in self.__parent.sub_elements
            ):
                self.__parent.remove(self)

            self.__parent = new_parent

        elif self.__parent is not None and new_parent != self.__parent:
            self.__parent.remove(self)

            self.__parent = new_parent
            if self not in new_parent.sub_elements:
                new_parent.append(self)
        else:
            self.__parent = new_parent

    def save(self):
        if self.__parent is not None:
            self.__parent.save()

    def insert(self, index, element):
        if (
            isinstance(element, XMLElement) and
            not isinstance(element, XMLRootElement) and
            element not in self.__children
        ):
            self.__children.insert(index, element)
            element.parent = self

            self.save()
            return True

        return False

    def append(self, element):
        if (
            isinstance(element, XMLElement) and
            not isinstance(element, XMLRootElement) and
            element not in self.__children
        ):
            self.__children += [element]
            element.parent = self

            self.save()
            return True

        return False

    def remove(self, element):
        if element in self.__children:
            self.__children.remove(element)
            element.parent = None
            self.save()
            return True

        return False

    def pop(self, index):
        if len(self.__children) > index:
            res = self.__children.pop(index)
            res.parent = None
            self.save()
            return res

    def __getitem__(self, key):
        if isinstance(key, (int, slice)):
            try:
                return self.__children[key]
            except:  # NOQA
                raise IndexError(key)

        try:
            return self.__attrib[key]
        except KeyError:
            raise KeyError(key)

    def __setitem__(self, key, value):
        if isinstance(key, (int, slice)):
            if isinstance(value, XMLElement):
                try:
                    self.__children[key] = value
                    value.parent = self
                except IndexError:
                    raise IndexError(key)

            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, XMLElement):
                        self.append(item)
                    else:
                        raise TypeError(
                            'Sub Element is not '
                            'XMLElement instance ({0})'.format(item)
                        )

            else:
                raise TypeError(
                    'Sub Element is not '
                    'XMLElement instance ({0})'.format(value)
                )
        else:
            self.__attrib[key] = value
            self.save()

    def __delitem__(self, key):
        if isinstance(key, (int, slice)):
            try:
                del self.__children[key]
                self.save()
            except IndexError:
                raise IndexError(key)
        else:
            try:
                del self.__attrib[key]
                self.save()
            except KeyError:
                raise KeyError(key)

    def __getattr__(self, key):
        if key in self.__dict__:
            return self.__dict__[key]

        if key in self.__class__.__dict__:
            obj = self.__class__.__dict__[key]
            fget = getattr(obj, 'fget', None)

            if fget is not None:
                return fget(self)

        if not key.isupper():
            try:
                return self[key]
            except KeyError:
                pass

        raise AttributeError(key)

    def __contains__(self, key):
        if key in self.__dict__:
            return True

        if key in self.__attrib:
            return True

        return False

    def __delattr__(self, item):
        if item not in self.__dict__:
            raise AttributeError('no such attribute (' + item + ')')

        obj = self.__dict__[item]
        if not isinstance(obj, XMLElement):
            raise AttributeError('unabo delete attribute (' + item + ')')

        self.remove(obj)
        del self.__dict__[item]

    def __setattr__(self, key, value):
        if key.startswith('_'):
            self.__dict__[key] = value

        elif key in self.__class__.__dict__:
            obj = self.__class__.__dict__[key]
            fset = getattr(obj, 'fset', None)

            if fset is not None:
                fset(self, value)

        elif isinstance(value, XMLElement):
            if not key.isalpha():
                raise ValueError(
                    'attribute name for an element needs to be camelcase.'
                )
            if ' ' in key:
                raise ValueError(
                    'attribute name for an element cannot contain any spaces.'
                )
            if not key[0].isupper():
                raise ValueError(
                    'attribute name for an element needs to be camelcase.'
                )
            if value.tag != key:
                raise ValueError(
                    'Attribute name and tag of the '
                    'xml element must be the same.'
                )
            parent = value.__class__.parent

            # noinspection PyArgumentList
            if parent.fget(value) != self:
                self.append(value)
                self.__dict__[key] = value

        elif not key.isupper():
            self[key] = value

        else:
            raise ValueError(
                'value is not an XMLElement instance '
                '({0}: {1})'.format(repr(key), repr(value))
            )


class XMLRootElement(XMLElement):

    def __init__(self, tag):
        self.__xml_file = None
        self.__is_dirty = False
        self.__lock = threading.RLock()
        XMLElement.__init__(self, tag)

    @property
    def xml_file(self):
        return self.__xml_file

    @xml_file.setter
    def xml_file(self, value):
        self.__xml_file = value

    @property
    def is_dirty(self):
        return self.__is_dirty

    def save(self):
        self.__is_dirty = True

    def write_file(self):
        with self.__lock:
            if self.xml_file is not None and self.__is_dirty:
                self.__is_dirty = False
                data = str(self)

                with open(self.xml_file, 'w') as f:
                    f.write(data)

    @staticmethod
    def handle_file(file_path):
        try:
            with open(file_path, 'r') as f:
                xml_data = f.read()

            root = XMLRootElement.from_string(xml_data)

            if xml_data:
                with open(file_path + '.backup', 'w') as f:
                    f.write(xml_data)
        except:  # NOQA
            if not os.path.exists(file_path + '.backup'):
                raise

            with open(file_path + '.backup', 'r') as f:
                xml_data = f.read()

            root = XMLRootElement.from_string(xml_data)

        root.xml_file = file_path
        return root


class XMLLoadError(Exception):
    pass


def load(obj, tag='Root'):
    if isinstance(obj, (BytesIO, StringIO)):
        obj.seek(0)
        data = obj.read()

        return XMLRootElement.from_string(data)

    elif os.path.exists(obj):
        return XMLRootElement.handle_file(obj)

    elif '<?xml version=' in obj:
        return XMLRootElement.from_string(obj)

    elif os.path.exists(os.path.dirname(obj)):
        elm = XMLRootElement(tag)
        elm.xml_file = obj
        return elm

    raise XMLLoadError
