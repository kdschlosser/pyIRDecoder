# This is a wrapper class around a raw ir code.
# It is simply designed to provide some additional methods
# to parse the code easier.


# manchester encoding
# This is a tad tricky because of how manchester encoding works.
# some of the burst pairs can actually contain the space from the
# pair before it and may also contain the mark for the pair after it.

# -----  ------  ----    ----  ------    ------  ------------
#     |  |    |  |  |    |  |  |    |    |    |  |
#     ----    ----  ------  ----    ------    ----
# in this example of an IR stream you have 4 timings
# that make up a 1 and a 0
# 0 = -444, +444
# 1 = +444, -444
# if you have a 1 that follows a 0 you end up with an ir encoding of
# -444, +444, +444, -444
# because we are only given on and off durations the above would be given to us as
# -444, +888, -444
#
# and if you have a 0 that follows a 1 you get
# +444, -888, +444.
# so if you have the following bit sequence 1, 0, 1, 0 you get this
# +444, -888, +888, -888, +444
# so the IR example above is going to be encoded as
# -444, +888, -444, +444, -888, +444, -444, +888, -888, +888, -444, +444
# in the example above I didn't take into account any lead in and lead out data.
# if a lead in ends in a mark or an on state. if the first bit has an on state for
# it's mark then the mark gets added to the number for the end of the lead in state.
# the same kind of rule applies to the lead out as well.
#
# the timings for the above example would be

# -444, +888, -444, +444, -888, +444, -444, +888, -888, +888, -444

# here is the same example The numbers on outside top and bottom are the actual timings
# the numbers on the inside top and bottom are the "doubled" marks and spaces split in half.

#         +888   +444   +444   +888      +888
#
#      +444 +444 +444   +444 +444 +444 +444 +444
# -----  ------  ----    ----  ------    ------  ------------
#     |  |    |  |  |    |  |  |    |    |    |  |
#     ----    ----  ------  ----    ------    ----
#    -444    -444 -444 -444 -444  -444 -444   -444
#
#    -444     -444   -888   -444    -888      -444
#
# now lets put that into order using the inside top and bottom numbers.
# -444, +444, +444, -444, +444, -444, -444, +444, -444, +444, +444, -444, -444, +444, +444, -444

# now break that into pairs.
# -444, +444
# +444, -444
# +444, -444
# -444, +444
# -444, +444
# +444, -444
# -444, +444
# +444, -444
#
# now match  the pairs to the pairs we assigned to be a 1 and a 0
# 0, 1, 1, 0, 0, 1, 0, 1
# all bits in a byte are read from right to left. the right most bit being bit 0.
# so for a number 1 the bits would be 0,0,0,0,0,0,0,1
#
# The data streams can be encoded so the data sent is msb (most significant bit) first or
# lsb (least significant bit) first
# what defines the 2 is the locations of the bits the number order they are coming in.
# for our example this is what msb and lsb do.
#
# msb bit numbers      7 6 5 4 3 2 1 0
#
# bit values           0 1 1 0 0 1 0 1
#
# lsb bit numbers      0 1 2 3 4 5 6 7
#
# so lsb and msb tell us what direction to read the bit numbers in. msb is how a typical number is encoded
# and how we read the bits, right to left
# lsb is left to right. We need to apply the bits so we would read them right to left. so with an lsb
# encoded ir signal we need to flip the whole sequence. so it would read.
# 1  0  1  0  0  1  1  0
#
# This ends up being a completely different decimal value then a stream encoded with msb.
# msb encoded = 101
# lsb encoded = 166
#
# we handle the reversing of the bits when collecting the parameters from the code.


import math
from . import DecodeError


class CodeWrapper(object):
    @property
    def encoding(self):
        return self._encoding

    @property
    def original_code(self):
        return self._original_code[:]

    @property
    def burst_pairs(self):
        return self._bursts[:]

    @property
    def tolerance(self):
        return self._tolerance

    @property
    def stream_encoding(self):
        return self._stream_encoding

    @property
    def stream_pairs(self):
        return self._stream_pairs[:]

    def __init__(self, encoding, lead_in, lead_out, middle_timings, bursts, tolerance, code):
        self._encoding = encoding
        self._original_code = code[:]
        self._lead_in = lead_in[:]
        self._lead_out = lead_out[:]
        self._bursts = bursts[:]
        self._tolerance = tolerance
        self._stream_encoding = 'halfbit'
        self._middle_timings = middle_timings[:]
        last_pair = bursts[0]
        total_time = sum(abs(item) for item in code[:-1])
        decoded_code = []
        cleaned_code = []
        pairs = []
        
        if isinstance(last_pair, int):
            self._stream_encoding = 'bit'
        else:
            for mark, space in bursts[1:]:
                if (
                    mark == last_pair[1] and
                    space == last_pair[0]
                ):
                    self._stream_encoding = 'manchester'
                    break

                last_pair = [mark, space]

        cleaned_lead_out = []
        half_bits = []
        offset = 0

        if self._stream_encoding == 'bit':
            for i, e_burst in enumerate(lead_in):
                burst = code[i - offset]
                if self._match(burst, e_burst):
                    code.pop(0)
                    cleaned_code += [e_burst]
                    offset += 1
                    continue

                for timing in bursts:
                    multiplier = (burst - e_burst) // timing
                    if multiplier == 0:
                        continue

                    if self._match(burst, timing * multiplier + e_burst):
                        offset += 1
                        code.pop(0)
                        code.insert(0, burst - e_burst)
                        cleaned_code += [e_burst]
                        break
                else:
                    raise DecodeError('Invalid lead in')

            for i, e_burst in enumerate(lead_out):
                idx = ~(i - len(lead_out)) + 1
                burst = code.pop(len(code) - idx)

                if self._match(burst, e_burst):
                    cleaned_lead_out += [e_burst]
                    continue

                if i == 0:
                    for timing in bursts:
                        multiplier = (burst - e_burst) // timing
                        if multiplier == 0:
                            continue

                        if self._match(burst, timing * multiplier + e_burst):
                            half_bits += [burst - e_burst]
                            cleaned_lead_out += [e_burst]
                            break
                    else:
                        raise DecodeError('Invalid lead out')

        else:
            for i, e_burst in enumerate(lead_in):
                burst = code[i - offset]
                if self._match(burst, e_burst):
                    code.pop(0)
                    cleaned_code += [e_burst]
                    offset += 1
                    continue

                for mark, _ in bursts:
                    if self._match(burst, e_burst + mark):
                        code.pop(0)
                        code.insert(0, mark)
                        cleaned_code += [e_burst]
                        offset += 1
                        break
                else:
                    for timing in middle_timings:
                        if not isinstance(timing, list):
                            continue

                        timing = timing[0]

                        if self._match(burst, e_burst + timing):
                            offset += 1
                            code.pop(0)
                            code.insert(0, timing)
                            cleaned_code += [e_burst]
                            break
                    else:
                        raise DecodeError('Invalid lead in')

            for i, e_burst in enumerate(lead_out):
                idx = ~(i - len(lead_out)) + 1
                burst = code.pop(len(code) - idx)

                if self._match(burst, e_burst):
                    cleaned_lead_out += [e_burst]
                    continue

                for _, space in bursts:
                    if len(lead_out) % 2 == 0 and i == 0 and self._match(burst - space, e_burst):
                        half_bits += [space]
                        cleaned_lead_out += [e_burst]
                        break

                    if i + 1 == len(lead_out) and space < 0 and self._match(burst + space, e_burst):
                        half_bits += [space]
                        cleaned_lead_out += [e_burst]
                        break
                else:
                    if self._match(e_burst, total_time + abs(burst)):
                        cleaned_lead_out += [None]

                    elif not cleaned_lead_out:
                        for _, space in bursts:
                            if e_burst < 0 > space and self._match(e_burst, burst - space):
                                cleaned_lead_out += [e_burst]
                                half_bits += [space]
                                break

                            if e_burst > 0 < space and self._match(e_burst, burst - space):
                                cleaned_lead_out += [e_burst]
                                half_bits += [space]
                                break
                        else:
                            raise DecodeError('Invalid lead out')

                    else:
                        raise DecodeError('Invalid lead out')

        code += half_bits[:]

        if self._stream_encoding == 'bit':
            mark, space = bursts

            for burst in code:
                multiplier = burst // mark

                if multiplier <= 0:
                    multiplier = burst // space
                    if multiplier <= 0:
                        raise DecodeError('Invalid burst')
                    timing = space

                else:
                    timing = mark

                if self._match(burst, timing * multiplier):
                    cleaned_code += [timing] * multiplier
                    pairs += [timing] * multiplier
                else:
                    raise DecodeError('Invalid burst')

        elif self._stream_encoding == 'manchester':
            mark, space = bursts[0]

            for i, burst in enumerate(code[:]):
                if self._match(burst, mark):
                    pairs += [mark]
                    cleaned_code += [mark]
                    continue

                if self._match(burst, space):
                    pairs += [space]
                    cleaned_code += [space]
                    continue

                for timing in middle_timings:
                    if isinstance(timing, dict):
                        if len(pairs) // 2 < timing['start'] - 1 or len(pairs) // 2 > timing['stop'] - 1:
                            continue

                        t_mark, t_space = timing['bursts'][0]

                        if self._match(burst, t_mark):
                            pairs += [t_mark]
                            cleaned_code += [t_mark]
                            break

                        if self._match(burst, t_space):
                            pairs += [t_space]
                            cleaned_code += [t_space]
                            break

                        if self._match(burst, t_mark * 2):
                            pairs += [t_mark, t_mark]
                            cleaned_code += [t_mark, t_mark]
                            break

                        if self._match(burst, t_space * 2):
                            pairs += [t_space, t_space]
                            cleaned_code += [t_space, t_space]
                            break

                        if self._match(burst, mark + t_mark):
                            if pairs[-1] == space:
                                pairs += [mark, t_mark]
                                cleaned_code += [mark, t_mark]
                                break
                            if pairs[-1] == t_space:
                                pairs += [t_mark, mark]
                                cleaned_code += [t_mark, mark]
                                break

                        if self._match(burst, space + t_space):
                            if pairs[-1] == mark:
                                pairs += [space, t_space]
                                cleaned_code += [space, t_space]
                                break
                            if pairs[-1] == t_mark:
                                pairs += [t_space, space]
                                cleaned_code += [t_space, space]
                                break

                else:
                    for timing in middle_timings[:]:
                        if isinstance(timing, dict):
                            continue

                        if isinstance(timing, tuple):
                            t_mark, t_space = timing

                            if cleaned_code[-1] == t_mark:
                                if self._match(burst, t_space):
                                    middle_timings.remove(timing)
                                    cleaned_code += [t_space]
                                    break
                                if self._match(burst, t_space * 2):
                                    pairs += [t_space]
                                    middle_timings.remove(timing)
                                    cleaned_code += [t_space, t_space]
                                    break

                                if self._match(burst, space + t_space):
                                    middle_timings.remove(timing)
                                    if pairs[-1] == mark:
                                        pairs += [space]
                                        cleaned_code += [space, t_space]
                                    else:
                                        pairs += [space]
                                        cleaned_code += [t_space, space]
                                    break

                            if self._match(burst, t_mark):
                                if self._match(code[i + 1], t_space):
                                    cleaned_code += [t_mark]
                                    break
                                if self._match(code[i + 1], t_space + space):
                                    cleaned_code += [t_mark]
                                    break

                            if self._match(burst, t_mark + mark):
                                if self._match(code[i + 1], t_space):
                                    cleaned_code += [mark, t_mark]
                                    pairs += [mark]
                                    break
                                if self._match(code[i + 1], t_space + space):
                                    cleaned_code += [mark, t_mark]
                                    pairs += [mark]
                                    break

                            else:
                                continue

                            break
                        elif self._match(burst, timing):
                            middle_timings.remove(timing)
                            cleaned_code += [timing]
                            break
                        elif timing < 0 > mark or timing > 0 < mark:
                            if self._match(burst, timing + mark):
                                pairs += [mark]
                                cleaned_code += [mark, timing]
                                middle_timings.remove(timing)
                                break

                            if self._match(burst, timing + (mark * 2)):
                                pairs += [mark, mark]
                                cleaned_code += [mark, timing, mark]
                                middle_timings.remove(timing)
                                break
                        elif timing < 0 > space or timing > 0 < space:
                            if self._match(burst, timing + space):
                                pairs += [space]
                                cleaned_code += [space, timing]
                                middle_timings.remove(timing)
                                break
                            if self._match(burst, timing + (space * 2)):
                                pairs += [space, space]
                                cleaned_code += [space, timing, space]
                                middle_timings.remove(timing)
                                break
                    else:
                        if self._match(burst, mark * 2):
                            pairs += [mark, mark]
                            cleaned_code += [mark, mark]

                        elif self._match(burst, space * 2):
                            pairs += [space, space]
                            cleaned_code += [space, space]

                        else:
                            raise DecodeError('Invalid burst')

            tmp = []

            extra_timings = list(timing['bursts'] for timing in middle_timings if isinstance(timing, dict))
            if extra_timings:
                extra_timings = extra_timings[0]

            for i in range(0, len(pairs), 2):
                mark = pairs[i]
                try:
                    space = pairs[i + 1]
                    if [mark, space] in extra_timings:
                        mark, space = bursts[extra_timings.index([mark, space])]

                    tmp += [[mark, space]]
                except IndexError:
                    tmp += [[mark]]

            pairs = tmp[:]

        else:

            def _check_middles():

                def _check_timing():
                    if (
                        self._match(burst, m) and
                        self._match(code[i + 1], s)
                    ):
                        cleaned_code.append(m)
                        return True
                    if (
                        self._match(burst, s) and
                        self._match(cleaned_code[-1], m) and
                        len(pairs[-1]) == 2
                    ):
                        cleaned_code.append(s)
                        if isinstance(timing, tuple):
                            middle_timings.remove(timing)
                        return True

                    if (
                        self._match(burst, m + space) and
                        self._match(code[i + 1], s) and
                        len(pairs[-1]) == 1
                    ):
                        pairs[-1].append(space)
                        cleaned_code.extend([space, m])
                        return True

                    if (
                        self._match(burst, s + mark) and
                        self._match(cleaned_code[-1], m) and
                        len(pairs[-1]) == 2
                    ):
                        pairs.append([mark])
                        cleaned_code.extend([s, mark])
                        return True

                    if (
                        cleaned_code[-1] == space and
                        self._match(burst, m)
                    ):
                        pairs.append([m])
                        cleaned_code.append(m)
                        return True

                    if (
                        cleaned_code[-1] == s and
                        self._match(burst, m)
                    ):
                        pairs.append([m])
                        cleaned_code.append(m)
                        return True

                    if (
                        cleaned_code[-1] == m and
                        self._match(burst, s)
                    ):
                        pairs[-1].append(s)
                        cleaned_code.append(s)
                        return True

                for timing in middle_timings:
                    if pairs and isinstance(timing, dict):
                        if len(pairs[-1]) == 2:
                            count = len(pairs)
                        else:
                            count = len(pairs) - 1

                        start = timing['start']
                        stop = timing['stop']

                        if count < start - 1 or count > stop:
                            continue

                        for m, s in timing['bursts']:
                            if _check_timing():
                                return True

                    elif isinstance(timing, tuple):
                        m, s = timing
                        if _check_timing():
                            return True
                        continue

                    if self._match(burst, timing):
                        cleaned_code.append(timing)
                        middle_timings.remove(timing)
                        return True
                    if self._match(burst, timing + mark):
                        cleaned_code.extend([timing, mark])
                        pairs.append([mark])
                        middle_timings.remove(timing)
                        return True
                    if self._match(burst, timing + space):
                        cleaned_code.extend([space, timing])
                        if len(pairs[-1]) == 1:
                            pairs[-1].append(space)
                        else:
                            pairs.append([space])
                        middle_timings.remove(timing)
                        return True

                return False

            for i, burst in enumerate(code):
                for mark, space in bursts:
                    if len(pairs) > 0:
                        if _check_middles():
                            break

                    if self._match(burst, mark):
                        if pairs and len(pairs[-1]) == 1:
                            pairs[-1] += [mark]
                        else:
                            pairs += [[mark]]

                        cleaned_code += [mark]
                        break
                    if self._match(burst, space):
                        if pairs and len(pairs[-1]) == 1:
                            pairs[-1] += [space]
                        else:
                            pairs += [[space]]

                        cleaned_code += [space]
                        break

                else:
                    raise DecodeError('Invalid pair (' + str(i) + ' : ' + str(burst) + ')\n' + str(code))

        for timing in middle_timings:
            if not isinstance(timing, dict):
                raise DecodeError('middle timings left over')

        for i, bp in enumerate(pairs):
            if self._stream_encoding != 'bit' and len(bp) == 1:
                if i + 1 == len(pairs):
                    for mark, space in bursts:
                        if bp[0] == mark:
                            bp += [space]
                            cleaned_code += [space]
                            break
                    else:
                        raise DecodeError('Invalid burst')
                else:
                    raise DecodeError('I really don\'t know what happened')

            if bp in bursts:
                decoded_code += [bursts.index(bp)]

            else:
                raise DecodeError('Invalid burst bair (', bp, ')')

        self._code = []
        cleaned_code += cleaned_lead_out

        if cleaned_code[-1] is None:
            total_time = -self._lead_out[-1]
            total_time += sum(abs(item) for item in cleaned_code[:-1])
            cleaned_code[-1] = total_time

        for pulse in cleaned_code:
            if len(self._code) and (self._code[-1] < 0 > pulse or self._code[-1] > 0 < pulse):
                self._code[-1] += pulse
                continue

            self._code += [pulse]

        self._stream_pairs = pairs[:]
        self._decoded_code = decoded_code[:]

    def _match_pair(self, mark, space, expected_mark, expected_space):
        return (
            self._match(mark, expected_mark) and
            self._match(space, expected_space)
        )

    def _match(self, value, expected_timing_value):
        if value < 0 < expected_timing_value or value > 0 > expected_timing_value:
            return False

        high = math.floor(expected_timing_value + (expected_timing_value * (self._tolerance / 100.0)))
        low = math.floor(expected_timing_value - (expected_timing_value * (self._tolerance / 100.0)))

        # do a flip flop of the high and low so the same expression can
        # be used when evaluating a raw timing
        if expected_timing_value < 0:
            low, high = high, low

        return low <= value <= high

    def __iter__(self):
        for item in self._code:
            yield item

    def __getitem__(self, item):
        return self._code[item]

    def get_value(self, start_bit, stop_bit):
        bits = self._decoded_code[start_bit: stop_bit + 1]

        if self._encoding.startswith('msb'):
            bits = list(bits[i] for i in range(len(bits) - 1, -1, -1))

        res = 0
        for i, item in enumerate(bits):
            res = self._set_bit(res, i, item)

        return res

    @staticmethod
    def _set_bit(value, bit_num, state):
        if state:
            return value | (1 << bit_num)
        else:
            return value & ~(1 << bit_num)

    @staticmethod
    def _get_bit(value, bit_num):
        return int(value & (1 << bit_num) > 0)

    @property
    def lead_in(self):
        return self._lead_in[:]

    @property
    def lead_out(self):

        lead_out = self._lead_out[:]
        if lead_out and lead_out[-1] > 0:
            tt = sum(abs(item) for item in self._code[:-1])
            lead_out[-1] = tt - lead_out[-1]

        return lead_out

    @property
    def num_bits(self):
        return len(self._decoded_code)

    @property
    def bits(self):
        return self._decoded_code[:]

    def get_burst_pair(self, index):
        return self._stream_pairs[index]