

import pyIRDecoder
import random

from pyIRDecoder import protocols


# These properties will tell you if these parameters are available
# as part of an IR code. The return value will be a min and max value that can
# be set or -1, -1 if it is not supported
print(protocols.Sony20.device)
print(protocols.Sony20.sub_device)
print(protocols.Sony20.function)
print(protocols.Sony20.extended_function)
print(protocols.Sony20.mode)
print(protocols.Sony20.oem1)
print(protocols.Sony20.oem2)
print(protocols.Sony20.toggle)


# you can also use the following property to get a list of [name, min, max]
# for the parameters. The names of the parameters match the parameter names
# used in the encode function for a protocol.
print(protocols.Sony20.encode_parameters)


# I am going to collect a random set of parameters to use
params = {}
for param, min_val, max_val in protocols.Sony20.encode_parameters:
    params[param] = random.randint(min_val, max_val)

print(params)


# if we want to encode an IR code for sending we can use the parameters
# above or manually enter the parameters

code = protocols.Sony20.encode(**params)
print(code)

code = protocols.Sony20.encode(device=23, sub_device=254, function=105)
print(code)

# the returned value is an IRCode instance. This instance contains several
# very useful properties. The same class gets returned when decoding as well.
# So these same properties apply as well.


# the original RLC code
print(code.original_rlc)

# the original RLC encoded as an MCE RLC (rounded to the nearest 50us)
print(code.original_rlc_mce)

# the original RLC as pronto code
print(code.original_rlc_pronto)

# the original RLC encoded to MCE and then to pronto code.
print(code.original_mce_pronto)


# this next group of properties are what you would use for transmitting the IR code.
# this is going to be a to spec version of the code. IR "learning" is eactly
# that. It takes the code it has received and that is what is used when sending
# The issue with this is IR is far from a perfect way of transmitting data and
# there are all kinds of things that can cause variations in the signal. This
# library make a to spec version of the IR code. so as it was intended to be
# not something that has been learned. This library takes it one step further
# by making a spec perfect IR code to send while it is decoding. This is ideal
# for range extender applications.

# These properties contain the spec versions of the IR code. The naming convention
# mirrors that of the original properties
print(code.normalized_rlc)
print(code.normalized_rlc_mce)
print(code.normalized_rlc_pronto)
print(code.normalized_mce_pronto)


# If you know the protocol you can speed up the decoding process by directly
# decoding a ir signal using that specific protocol

code = protocols.decode(code.normalized_rlc[0], code.frequency)

print(code)

# if you do not know the protocol you can have the library attempt to match a
# protocol with the code.


code = protocols.decode(code.original_rlc, code.frequency)

print(code)

# frequency
# device
# sub_device
# function
# extended_function
# mode
# oem
# oem1
# oem2
# toggle
# u
# x
# g
# n
# checksum
#
#
#
# hexadecimal
# decoder
#
#
# bind_released_callback
# unbind_released_callback
#

