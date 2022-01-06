from typing import Union, Optional


class IntegerWrapper(object):

    def __init__(
            self,
            value: Union[int, "IntegerWrapper"],
            num_bits: Optional[int] = None,
            timings: Optional[list] = None,
            encoding: Optional[str] = None
    ):
        if isinstance(value, IntegerWrapper):
            if num_bits is None:
                num_bits = value.num_bits
                value = int(value)
            else:
                value = int(value)
                if value >= 0:
                    val = 0
                    for i in range(num_bits):
                        val |= ((value >> i) & 1) << i

                    value = val
        else:
            if num_bits is None:
                if value == 0:
                    num_bits = 1
                else:
                    num_bits = value.bit_length()
            else:
                if value >= 0:
                    val = 0
                    for i in range(num_bits):
                        val |= ((value >> i) & 1) << i

                    value = val

        self._num_bits = num_bits
        self._value = value
        self._timings = timings
        self.encoding = encoding

    def __eq__(self, other: Union[int, "IntegerWrapper"]):  # self ==
        if isinstance(other, IntegerWrapper):
            other = int(other)

        return self._value == other

    def __ne__(self, other: Union[int, "IntegerWrapper"]):  # self !=
        if isinstance(other, IntegerWrapper):
            other = int(other)

        return self._value != other

    def __lt__(self, other: Union[int, "IntegerWrapper"]):  # self <
        if isinstance(other, IntegerWrapper):
            other = int(other)

        return self._value < other

    def __gt__(self, other: Union[int, "IntegerWrapper"]):  # self >
        if isinstance(other, IntegerWrapper):
            other = int(other)

        return self._value > other

    def __le__(self, other: Union[int, "IntegerWrapper"]):  # self <=
        if isinstance(other, IntegerWrapper):
            other = int(other)

        return self._value <= other

    def __ge__(self, other: Union[int, "IntegerWrapper"]):  # self >=
        if isinstance(other, IntegerWrapper):
            other = int(other)

        return self._value >= other

    def __pos__(self):  # +self
        return IntegerWrapper(
            +self._value,
            self.num_bits,
            self._timings,
            self.encoding
        )

    def __neg__(self):  # -self
        return IntegerWrapper(
            -self._value,
            self.num_bits,
            self._timings,
            self.encoding
        )

    def __abs__(self):  # abs(self)
        return IntegerWrapper(
            abs(self._value),
            self.num_bits,
            self._timings,
            self.encoding
        )

    def __invert__(self):  # ~self
        return IntegerWrapper(
            ~self._value,
            timings=self._timings,
            encoding=self.encoding
        )

    def __add__(self, other: Union[int, "IntegerWrapper"]):  # self +
        if isinstance(other, IntegerWrapper):
            other_num_bits = other.num_bits
            other = int(other)
        else:
            other_num_bits = other.bit_length()

        return IntegerWrapper(
            self._value + other,
            timings=self._timings,
            encoding=self.encoding
        )

    def __sub__(self, other: Union[int, "IntegerWrapper"]):  # self -
        if isinstance(other, IntegerWrapper):
            other = int(other)

        return IntegerWrapper(
            self._value - other,
            timings=self._timings,
            encoding=self.encoding
        )

    def __mul__(self, other: Union[int, "IntegerWrapper"]):  # self *
        if isinstance(other, IntegerWrapper):
            other = int(other)

        return IntegerWrapper(
            self._value * other,
            timings=self._timings,
            encoding=self.encoding
        )

    def __floordiv__(self, other: Union[int, "IntegerWrapper"]):  # self //
        if isinstance(other, IntegerWrapper):
            other = int(other)

        return IntegerWrapper(
            self._value // other,
            timings=self._timings,
            encoding=self.encoding
        )

    def __div__(self, other: Union[int, "IntegerWrapper"]):  # self /
        if isinstance(other, IntegerWrapper):
            other = int(other)

        return IntegerWrapper(
            self._value // other,
            timings=self._timings,
            encoding=self.encoding
        )

    def __truediv__(self, other: Union[int, "IntegerWrapper"]):  # self /
        if isinstance(other, IntegerWrapper):
            other = int(other)

        return IntegerWrapper(
            self._value // other,
            timings=self._timings,
            encoding=self.encoding
        )

    def __mod__(self, other: Union[int, "IntegerWrapper"]):  # self %
        if isinstance(other, IntegerWrapper):
            other = int(other)

        return IntegerWrapper(
            self._value % other,
            timings=self._timings,
            encoding=self.encoding
        )

    def __lshift__(self, other: Union[int, "IntegerWrapper"]):  # self <<
        if isinstance(other, IntegerWrapper):
            other = int(other)

        return IntegerWrapper(
            self._value << other,
            self._num_bits + other,
            self._timings,
            self.encoding
        )

    def __rshift__(self, other: Union[int, "IntegerWrapper"]):  # self >>
        if isinstance(other, IntegerWrapper):
            other = int(other)

        return IntegerWrapper(
            self._value >> other,
            self._num_bits - other,
            self._timings,
            self.encoding
        )

    def __and__(self, other: Union[int, "IntegerWrapper"]):  # self &
        if isinstance(other, IntegerWrapper):
            other = int(other)

        return IntegerWrapper(
            self._value & other,
            timings=self._timings,
            encoding=self.encoding
        )

    def __or__(self, other: Union[int, "IntegerWrapper"]):  # self |
        if isinstance(other, IntegerWrapper):
            other = int(other)

        return IntegerWrapper(
            self._value | other,
            timings=self._timings,
            encoding=self.encoding
        )

    def __xor__(self, other: Union[int, "IntegerWrapper"]):  # self ^
        if isinstance(other, IntegerWrapper):
            other = int(other)

        return IntegerWrapper(
            self._value ^ other,
            timings=self._timings,
            encoding=self.encoding
        )

    def __radd__(self, other: Union[int, "IntegerWrapper"]):  # + self
        if isinstance(other, IntegerWrapper):
            other = int(other)

        return IntegerWrapper(
            other + self._value,
            timings=self._timings,
            encoding=self.encoding
        )

    def __rsub__(self, other: Union[int, "IntegerWrapper"]):  # - self
        if isinstance(other, IntegerWrapper):
            other = int(other)

        return IntegerWrapper(
            other - self._value,
            timings=self._timings,
            encoding=self.encoding
        )

    def __rmul__(self, other: Union[int, "IntegerWrapper"]):  # * self
        if isinstance(other, IntegerWrapper):
            other = int(other)

        return IntegerWrapper(
            other * self._value,
            timings=self._timings,
            encoding=self.encoding
        )

    def __rfloordiv__(self, other: Union[int, "IntegerWrapper"]):  # // self
        if isinstance(other, IntegerWrapper):
            other = int(other)

        return IntegerWrapper(
            other // self._value,
            timings=self._timings,
            encoding=self.encoding
        )

    def __rdiv__(self, other: Union[int, "IntegerWrapper"]):  # / self
        if isinstance(other, IntegerWrapper):
            other = int(other)

        return IntegerWrapper(
            other // self._value,
            timings=self._timings,
            encoding=self.encoding
        )

    def __rtruediv__(self, other: Union[int, "IntegerWrapper"]):  # / self
        if isinstance(other, IntegerWrapper):
            other = int(other)

        return IntegerWrapper(
            other // self._value,
            timings=self._timings,
            encoding=self.encoding
        )

    def __rmod__(self, other: Union[int, "IntegerWrapper"]):  # % self
        if isinstance(other, IntegerWrapper):
            other = int(other)

        return IntegerWrapper(
            other % self._value,
            timings=self._timings,
            encoding=self.encoding
        )

    def __rlshift__(self, other: Union[int, "IntegerWrapper"]):  # << self
        if isinstance(other, IntegerWrapper):
            other_num_bits = other.num_bits
            other = int(other)
        else:
            other_num_bits = other.bit_length()

        return IntegerWrapper(
            other << self._value,
            other_num_bits + self._num_bits,
            self._timings,
            self.encoding
        )

    def __rrshift__(self, other: Union[int, "IntegerWrapper"]):  # >> self
        if isinstance(other, IntegerWrapper):
            other_num_bits = other.num_bits
            other = int(other)
        else:
            other_num_bits = other.bit_length()

        return IntegerWrapper(
            other >> self._value,
            other_num_bits - self._num_bits,
            self._timings,
            self.encoding
        )

    def __rand__(self, other: Union[int, "IntegerWrapper"]):  # & self
        if isinstance(other, IntegerWrapper):
            other_num_bits = other.num_bits
            other = int(other)
        else:
            other_num_bits = other.bit_length()

        return IntegerWrapper(
            other & self._value,
            max(self._num_bits, other_num_bits),
            self._timings,
            self.encoding
        )

    def __ror__(self, other: Union[int, "IntegerWrapper"]):  # | self
        if isinstance(other, IntegerWrapper):
            other_num_bits = other.num_bits
            other = int(other)
        else:
            other_num_bits = other.bit_length()

        return IntegerWrapper(
            other | self._value,
            max(self._num_bits, other_num_bits),
            self._timings,
            self.encoding
        )

    def __rxor__(self, other: Union[int, "IntegerWrapper"]):  # ^ self
        if isinstance(other, IntegerWrapper):
            other_num_bits = other.num_bits
            other = int(other)
        else:
            other_num_bits = other.bit_length()

        return IntegerWrapper(
            other ^ self._value,
            max(self._num_bits, other_num_bits),
            self._timings,
            self.encoding
        )

    def __iadd__(self, other: Union[int, "IntegerWrapper"]):  # self +=
        if isinstance(other, IntegerWrapper):
            other = int(other)

        self._value += other
        self._num_bits = self._value.bit_length()
        return self

    def __isub__(self, other: Union[int, "IntegerWrapper"]):  # self -=
        if isinstance(other, IntegerWrapper):
            other = int(other)

        self._value -= other
        self._num_bits = min(self._num_bits, self._value.bit_length())
        return self

    def __imul__(self, other: Union[int, "IntegerWrapper"]):  # self *=
        if isinstance(other, IntegerWrapper):
            other = int(other)

        self._value *= other
        self._num_bits = max(self._num_bits, self._value.bit_length())
        return self

    def __ifloordiv__(self, other: Union[int, "IntegerWrapper"]):  # self //=
        if isinstance(other, IntegerWrapper):
            other = int(other)

        self._value //= other
        self._num_bits = max(self._num_bits, self._value.bit_length())
        return self

    def __idiv__(self, other: Union[int, "IntegerWrapper"]):  # self /=
        if isinstance(other, IntegerWrapper):
            other = int(other)

        self._value //= other
        self._num_bits = max(self._num_bits, self._value.bit_length())
        return self

    def __itruediv__(self, other: Union[int, "IntegerWrapper"]):  # self /=
        if isinstance(other, IntegerWrapper):
            other = int(other)

        self._value //= other
        self._num_bits = max(self._num_bits, self._value.bit_length())
        return self

    def __imod__(self, other: Union[int, "IntegerWrapper"]):  # self %=
        if isinstance(other, IntegerWrapper):
            other = int(other)

        self._value %= other
        self._num_bits = max(self._num_bits, self._value.bit_length())
        return self

    def __ilshift__(self, other: Union[int, "IntegerWrapper"]):  # self <<=
        if isinstance(other, IntegerWrapper):
            other = int(other)

        self._value <<= other
        self._num_bits += other
        return self

    def __irshift__(self, other: Union[int, "IntegerWrapper"]):  # self >>=
        if isinstance(other, IntegerWrapper):
            other = int(other)

        self._value >>= other
        self._num_bits -= other
        return self

    def __iand__(self, other: Union[int, "IntegerWrapper"]):  # self &=
        if isinstance(other, IntegerWrapper):
            other_num_bits = other.num_bits
            other = int(other)
        else:
            other_num_bits = other.bit_length()

        self._value &= other
        self._num_bits = max(self._num_bits, other_num_bits)
        return self

    def __ior__(self, other: Union[int, "IntegerWrapper"]):  # self |=

        if isinstance(other, IntegerWrapper):
            other_num_bits = other.num_bits
            other = int(other)
        else:
            other_num_bits = other.bit_length()

        self._value |= other
        self._num_bits = max(self._num_bits, other_num_bits)
        return self

    def __ixor__(self, other: Union[int, "IntegerWrapper"]):  # self ^=
        if isinstance(other, IntegerWrapper):
            other_num_bits = other.num_bits
            other = int(other)
        else:
            other_num_bits = other.bit_length()

        self._value ^= other
        self._num_bits = max(self._num_bits, other_num_bits)
        return self

    def __int__(self):  # return self._value
        return self._value

    def __str__(self):  # str(self._value)
        return str(self._value)

    def __hash__(self):  # hash(self._value)
        return hash(self._value)

    def __len__(self):  # number of bits
        return self.num_bits

    def __hex__(self):
        return hex(self._value)

    def __setitem__(self, item, value):
        if isinstance(item, int):
            self._value |= value << item
            self._num_bits = max(self._num_bits, item + 1)

        elif isinstance(item, slice):
            num_bits = item.stop
            start_bit = item.step
            if start_bit is None:
                start_bit = 0

            for i in range(start_bit, start_bit + num_bits + 1):
                self._value |= ((value >> (i - start_bit)) & 1) << i

            self._num_bits = max(self._num_bits, start_bit + num_bits)

    def __getitem__(self, item):
        if not isinstance(item, slice):
            if isinstance(item, IntegerWrapper):
                item = int(item)

            return list(self)[item]

        if (
                item.stop is not None is not item.step and
                item.step != 0 <= item.stop
        ):
            val = IntegerWrapper(0)
            for i in range(item.step, item.step + item.stop + 1):
                val |= ((self >> i) & 0x1) << (i - item.step)

            val = IntegerWrapper(
                val,
                item.stop,
                self._timings,
                self.encoding
            )

        elif item.stop is not None and item.stop > 0:
            val = IntegerWrapper(0)
            for i in range(item.stop):
                val |= ((self >> i) & 0x1) << i

            val = IntegerWrapper(
                val,
                item.stop,
                self._timings,
                self.encoding
            )

        elif item.stop is not None and item.stop < 0:
            val = IntegerWrapper(0)
            if item.step is not None and item.step > 0:
                for i in range(item.step, item.step - item.stop + 1):
                    val |= ((self >> i) & 0x1) << (i - item.step)
            else:
                for i in range(-item.stop):
                    val |= ((self >> i) & 0x1) << i

            val = reversed(IntegerWrapper(
                val,
                -item.stop,
                self._timings,
                self.encoding
            ))

        elif item.stop is None and item.step is not None:
            val = IntegerWrapper(0)
            for i in range(item.step, len(self), 1):
                val |= ((self >> i) & 0x1) << i

            val = IntegerWrapper(
                val,
                len(self) - item.step,
                self._timings,
                self.encoding
            )
        else:
            val = self

        if item.start is True:
            return val.invert_bits()

        if item.start is not None:
            if item.start < 0:
                return item.start == ~val
            else:
                return item.start == val

        return val

    def __iter__(self):  # iterate over bits
        for i in range(self._num_bits):
            yield int((self >> i) & 1)

    def __reversed__(self):  # reverse bit order
        num_bits = self._num_bits

        val = 0

        for i in range(num_bits):
            val |= (int(self >> i) & 1) << (~i + num_bits)

        return IntegerWrapper(
            val,
            num_bits,
            self._timings,
            self.encoding
        )

    # isinstance(self, other)
    def __instancecheck__(self, instance: Union[int, "IntegerWrapper"]):
        if instance.__class__ in (int, IntegerWrapper):
            return True

        return False

    def __nonzero__(self):  # if self
        return self._num_bits != 0

    def __bool__(self):  # if self
        return self._num_bits != 0

    def invert_bits(self, num_bits=None):
        if num_bits is None:
            num_bits = self._num_bits
        elif isinstance(num_bits, IntegerWrapper):
            num_bits = int(num_bits)

        val = 0

        for i in range(num_bits):
            val |= (1 - (int(self >> i) & 1)) << i

        return IntegerWrapper(
            val,
            num_bits,
            self._timings,
            self.encoding
        )

    def reverse_bit_order(self, num_bits=None):
        if num_bits is None:
            num_bits = self._num_bits
        elif isinstance(num_bits, IntegerWrapper):
            num_bits = int(num_bits)

        val = 0

        for i in range(num_bits):
            val |= (int(self >> i) & 1) << (~i + num_bits)

        return IntegerWrapper(
            val,
            num_bits,
            self._timings,
            self.encoding
        )

    @property
    def num_one_bits(self):
        count = 0

        for i in range(self._num_bits):
            count += self._value >> i & 1

        count = IntegerWrapper(
            count,
            timings=self._timings,
            encoding=self.encoding
        )

        return count

    @property
    def timings(self):
        if self._timings is None:
            raise RuntimeError

        if self.encoding == 'msb':
            bits = self.bits
            if len(self._timings) == 4:
                needed = len(bits) % 2
            elif len(self._timings) > 4:
                needed = len(bits ) %4
            else:
                needed = 0
            for _ in range(needed):
                bits.insert(0, 0)
        else:
            bits = list(self)
            if len(self._timings) == 4:
                needed = len(bits) % 2
            elif len(self._timings) > 4:
                needed = len(bits) % 4
            else:
                needed = 0
            for _ in range(needed):
                bits.append(0)

        res = []
        if len(self._timings) == 2:
            for bit in bits:
                res.append(self._timings[bit])
        elif len(self._timings) == 4:
            for i in range(0, len(bits), 2):
                bit = bits[i] << 1 | bits[i + 1]
                res.append(self._timings[bit])
        else:
            for i in range(0, len(bits), 4):
                bit = bits[i] << 3 | bits[i + 1] << 2 | bits[i + 2] << 1 | bits[i + 3]
                res.append(self._timings[bit])

        def flatten(items):
            r = []
            for item in items:
                if isinstance(item, list):
                    r.extend(flatten(item))
                else:
                    r.append(item)

            ret = []
            for itm in r:
                if len(ret) > 0:
                    if itm > 0 < ret[-1] or itm < 0 > ret[-1]:
                        ret[-1] += itm
                    else:
                        ret.append(itm)
                else:
                    ret.append(itm)

            return ret

        return res

    @property
    def bits(self):
        bits = []
        for bit in self:
            bits.insert(0, bit)

        return bits

    @property
    def num_bits(self):
        return self._num_bits

    def __repr__(self):
        return repr(self._value)
