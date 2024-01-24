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


# in this example I am loading the modules from "test_protocols" so to see how
# things are done then check those files.
#
#
# The returned value from a successful decode is going to be an IRCode instance
# this instance has manu useful functions and properties.
# functions
#
# bind_released_callback(callback): bind a callback function for when the button gets released
# unbind_released_callback(callback)L unbind the callback function
#
# repeat_count: number of times the code has repeated
# params: list of the parameters the code has
# decoder: the protocol class used to decode the code
# frequency: IR signal frequency

#
# converted ir codes
#
# original_rlc: oriinal RLC that was decoded
# normalized_rlc: Normalized RLC to match protocol specification
# original_rlc_pronto: pronto code from the original RLC
# normalized_rlc_pronto: pronto code from the normalized RLC
# original_rlc_mce: original RLC rounded to the nearest 50us
# original_mce_pronto: pronto code of the original mce rlc
# normalized_rlc_mce: rlc normalized and then rounded to the nearest 50 us
# normalized_mce_pronto: rlc normalized and then rounded to the nearest 50 us converted to pronto code
#
# below are the different attribute a code may have. In order to know what
# attributes your code has use the params property to collect the list. of supported codes
#
# device
# sub_device
# function
# toggle
# mode
# n
# g
# address
# x
# extended_function
# u
# oem
# oem1
# oem2
#
# additional properties that may be useful
#
# name: name of the code
# hexadecimal: hex of the numberic value of the code


from __future__ import print_function
import random
import traceback
import threading
from pyIRDecoder import high_precision_timers
from pyIRDecoder import protocols
import os

ir_decoder = protocols.decode

decoding_times = []

failures = []
skipped = []
universals = []
repeat_error = []
decode_error = []
success = []


class ProtocolBase(object):
    enabled = True

    @classmethod
    def is_enabled(cls):
        return cls.enabled

    @classmethod
    def enable(cls, value):
        cls.enabled = value
        getattr(protocols, cls.__name__).enabled = value

    @classmethod
    def test(cls):
        try:
            if not cls.is_enabled():
                print('skipping', cls.__name__)
                skipped.append(cls.__name__)
                return

            def get_file_name(cls_name, check_num=False):
                last_last_char = ''
                last_char = ''
                res = ''
                for char in cls_name:
                    if (
                        res and
                        char.islower() and
                        last_char and
                        last_char.isupper() and not last_last_char.isupper()
                    ):
                        res += '_' + last_char.lower()
                    elif res and check_num and last_char.isdigit() and not res[-1].isdigit():
                        res += '_' + last_char
                    elif last_char:
                        res += last_char.lower()

                    last_last_char = last_char
                    last_char = char

                if last_char.isupper() and not last_last_char.isupper():
                    res += '_'
                res += last_char.lower()

                return 'test_' + res
            print(cls.__name__)
            mod_name = get_file_name(cls.__name__)
            try:
                mod = getattr(__import__('test_protocols', fromlist=(mod_name,)), mod_name)
            except:
                mod_name = get_file_name(cls.__name__, check_num=True)
                try:
                    mod = getattr(__import__('test_protocols', fromlist=(mod_name,)), mod_name)
                except:
                    mod_name = 'test_' + cls.__name__.lower()
                    mod = getattr(__import__('test_protocols', fromlist=(mod_name,)), mod_name)

            test_cls = mod.__dict__[cls.__name__]

            print('encoding', cls.__name__)
            print('parameters:', test_cls.params)

            start = high_precision_timers.TimerUS()
            mod.test_encode()
            stop = start.elapsed()

            print('encoding duration:', stop, 'us')
            print()

            start.reset()

            print('decoding', cls.__name__)
            print('rlc:', test_cls.rlc)
            print()
            mod.test_decode()
            stop = start.elapsed()

            print('decoding duration:', stop, 'us')
            print()
            
            success.append(cls.__name__)
        except:
            failures.append((cls.__name__, traceback.format_exc()))
            print()
            print()
            print()


class AdNotham(ProtocolBase):
    pass


class Aiwa(ProtocolBase):
    pass


class Akai(ProtocolBase):
    pass


class Akord(ProtocolBase):
    pass


class Amino(ProtocolBase):
    pass


class Amino56(ProtocolBase):
    pass


class Anthem(ProtocolBase):
    pass


class Apple(ProtocolBase):
    pass


class Archer(ProtocolBase):
    pass


class Arctech(ProtocolBase):
    pass


class Arctech38(ProtocolBase):
    pass


class Audiovox(ProtocolBase):
    pass


class Barco(ProtocolBase):
    pass


class Blaupunkt(ProtocolBase):
    pass


class Bose(ProtocolBase):
    pass


class Bryston(ProtocolBase):
    pass


class CanalSat(ProtocolBase):
    pass


class CanalSatLD(ProtocolBase):
    pass


class Denon(ProtocolBase):
    pass


class DenonK(ProtocolBase):
    pass


class Dgtec(ProtocolBase):
    pass


class Digivision(ProtocolBase):
    pass


class DirecTV(ProtocolBase):
    pass


class DirecTV0(ProtocolBase):
    pass


class DirecTV1(ProtocolBase):
    pass


class DirecTV2(ProtocolBase):
    pass


class DirecTV3(ProtocolBase):
    pass


class DirecTV4(ProtocolBase):
    pass


class DirecTV5(ProtocolBase):
    pass


class DishNetwork(ProtocolBase):
    pass


class DishPlayer(ProtocolBase):
    pass


class Dyson(ProtocolBase):
    pass


class Dyson2(ProtocolBase):
    pass


class Elan(ProtocolBase):
    pass


class Elunevision(ProtocolBase):
    pass


class Emerson(ProtocolBase):
    pass


class Entone(ProtocolBase):
    pass


class F12(ProtocolBase):
    pass


class F120(ProtocolBase):
    pass


class F121(ProtocolBase):
    pass


class F32(ProtocolBase):
    pass


class Fujitsu(ProtocolBase):
    pass


class Fujitsu128(ProtocolBase):
    pass


class Fujitsu56(ProtocolBase):
    pass


class GI4DTV(ProtocolBase):
    pass


class GICable(ProtocolBase):
    pass


class GIRG(ProtocolBase):
    pass


class Grundig16(ProtocolBase):
    pass


class Grundig1630(ProtocolBase):
    pass


class GuangZhou(ProtocolBase):
    pass


class GwtS(ProtocolBase):
    pass


class GXB(ProtocolBase):
    pass


class Humax4Phase(ProtocolBase):
    pass


class InterVideoRC201(ProtocolBase):
    pass


class IODATAn(ProtocolBase):
    pass


class Jerrold(ProtocolBase):
    pass


class JVC(ProtocolBase):
    pass


class JVC48(ProtocolBase):
    pass


class JVC56(ProtocolBase):
    pass


class Kaseikyo(ProtocolBase):
    pass


class Kaseikyo56(ProtocolBase):
    pass


class Kathrein(ProtocolBase):
    pass


class Konka(ProtocolBase):
    pass


class Logitech(ProtocolBase):
    pass


class Lumagen(ProtocolBase):
    pass


class Lutron(ProtocolBase):
    pass


class Matsui(ProtocolBase):
    pass


class MCE(ProtocolBase):
    pass


class MCIR2kbd(ProtocolBase):
    pass


class MCIR2mouse(ProtocolBase):
    pass


class Metz19(ProtocolBase):
    pass


class Mitsubishi(ProtocolBase):
    pass


class MitsubishiK(ProtocolBase):
    pass


class Motorola(ProtocolBase):
    pass


class NEC(ProtocolBase):
    pass


class NEC48(ProtocolBase):
    pass


class NECf16(ProtocolBase):
    pass


class NECrnc(ProtocolBase):
    pass


class NECx(ProtocolBase):
    pass


class NECxf16(ProtocolBase):
    pass


class Nokia(ProtocolBase):
    pass


class Nokia12(ProtocolBase):
    pass


class Nokia32(ProtocolBase):
    pass


class NovaPace(ProtocolBase):
    pass


class NRC16(ProtocolBase):
    pass


class NRC1632(ProtocolBase):
    pass


class NRC17(ProtocolBase):
    pass


class Ortek(ProtocolBase):
    pass


class OrtekMCE(ProtocolBase):
    pass


class PaceMSS(ProtocolBase):
    pass


class Panasonic(ProtocolBase):
    pass


class Panasonic2(ProtocolBase):
    pass


class PanasonicOld(ProtocolBase):
    pass


class PCTV(ProtocolBase):
    pass


class PID0001(ProtocolBase):
    pass


class PID0003(ProtocolBase):
    pass


class PID0004(ProtocolBase):
    pass


class PID0083(ProtocolBase):
    pass


class Pioneer(ProtocolBase):
    pass


class Proton(ProtocolBase):
    pass


class Proton40(ProtocolBase):
    pass


class RC5(ProtocolBase):
    pass


class RC57F(ProtocolBase):
    pass


class RC57F57(ProtocolBase):
    pass


class RC5x(ProtocolBase):
    pass


class RC6(ProtocolBase):
    pass


class RC6620(ProtocolBase):
    pass


class RC6624(ProtocolBase):
    pass


class RC6632(ProtocolBase):
    pass


class RC6M16(ProtocolBase):
    pass


class RC6M28(ProtocolBase):
    pass


class RC6M32(ProtocolBase):
    pass


class RC6M56(ProtocolBase):
    pass


class RC6MBIT(ProtocolBase):
    pass


class RCA(ProtocolBase):
    pass


class RCA38(ProtocolBase):
    pass


class RCA38Old(ProtocolBase):
    pass


class RCAOld(ProtocolBase):
    pass


class RCMM(ProtocolBase):
    pass


class RECS800045(ProtocolBase):
    pass


class RECS800068(ProtocolBase):
    pass


class RECS800090(ProtocolBase):
    pass


class Revox(ProtocolBase):
    pass


class Roku(ProtocolBase):
    pass


class Rs200(ProtocolBase):
    pass


class RTIRelay(ProtocolBase):
    pass


class Sampo(ProtocolBase):
    pass


class Samsung20(ProtocolBase):
    pass


class Samsung36(ProtocolBase):
    pass


class SamsungSMTG(ProtocolBase):
    pass


class ScAtl6(ProtocolBase):
    pass


class Sharp(ProtocolBase):
    pass


class Sharp1(ProtocolBase):
    pass


class Sharp2(ProtocolBase):
    pass


class SharpDVD(ProtocolBase):
    pass


class SIM2(ProtocolBase):
    pass


class Sky(ProtocolBase):
    pass


class SkyHD(ProtocolBase):
    pass


class SkyPlus(ProtocolBase):
    pass


class Somfy(ProtocolBase):
    pass


class Sony12(ProtocolBase):
    pass


class Sony15(ProtocolBase):
    pass


class Sony20(ProtocolBase):
    pass


class Sony8(ProtocolBase):
    pass


class StreamZap(ProtocolBase):
    pass


class StreamZap57(ProtocolBase):
    pass


class Sunfire(ProtocolBase):
    pass


class TDC38(ProtocolBase):
    pass


class TDC56(ProtocolBase):
    pass


class TeacK(ProtocolBase):
    pass


class Thomson(ProtocolBase):
    pass


class Thomson7(ProtocolBase):
    pass


class Tivo(ProtocolBase):
    pass


class Velleman(ProtocolBase):
    pass


class Viewstar(ProtocolBase):
    pass

#
# class Whynter(ProtocolBase):
#     decoder = ir_decoder.Whynter
#     encoder = ir_encoder.Whynter
#

class Zaptor36(ProtocolBase):
    pass


class Zaptor56(ProtocolBase):
    pass


class XBox360(ProtocolBase):
    pass


class XBoxOne(ProtocolBase):
    pass


if __name__ == '__main__':
    run_start = high_precision_timers.TimerUS()
    run_start.reset()

    AdNotham.test()
    Aiwa.test()
    Akai.test()
    Akord.test()
    Amino.test()
    Amino56.test()
    Anthem.test()
    Apple.test()
    Archer.test()
    Arctech.test()
    Arctech38.test()
    Barco.test()
    Bose.test()
    Bryston.test()
    CanalSat.test()
    CanalSatLD.test()
    Denon.test()
    DenonK.test()
    Dgtec.test()
    Digivision.test()
    DirecTV.test()
    DirecTV0.test()
    DirecTV1.test()
    DirecTV2.test()
    DirecTV3.test()
    DirecTV4.test()
    DirecTV5.test()
    DishNetwork.test()
    DishPlayer.test()
    Dyson.test()
    Dyson2.test()
    Elan.test()
    Elunevision.test()
    Emerson.test()
    Entone.test()
    F12.test()
    F120.test()
    F121.test()
    F32.test()
    Fujitsu.test()
    Fujitsu128.test()
    Fujitsu56.test()
    # GI4DTV.test()
    GICable.test()
    GIRG.test()
    # Grundig16.test()
    # Grundig1630.test()
    GuangZhou.test()
    GwtS.test()
    GXB.test()
    Humax4Phase.test()
    InterVideoRC201.test()
    IODATAn.test()
    Jerrold.test()
    JVC.test()
    JVC48.test()
    JVC56.test()
    Kaseikyo.test()
    Kaseikyo56.test()
    Kathrein.test()
    Konka.test()
    Logitech.test()
    Lumagen.test()
    Lutron.test()
    Matsui.test()
    MCE.test()
    MCIR2kbd.test()
    MCIR2mouse.test()
    Metz19.test()
    Mitsubishi.test()
    MitsubishiK.test()
    Motorola.test()
    NEC.test()
    NEC48.test()
    NECf16.test()
    NECx.test()
    NECxf16.test()
    Nokia.test()
    Nokia12.test()
    Nokia32.test()
    NovaPace.test()
    NRC16.test()
    NRC1632.test()
    NRC17.test()
    Ortek.test()
    OrtekMCE.test()
    PaceMSS.test()
    Panasonic.test()
    Panasonic2.test()
    PanasonicOld.test()
    PCTV.test()
    PID0001.test()
    PID0003.test()
    PID0004.test()
    PID0083.test()
    Pioneer.test()
    Proton.test()
    Proton40.test()
    RC5.test()
    RC57F.test()
    RC57F57.test()
    RC5x.test()
    RC6.test()
    RC6620.test()
    RC6624.test()
    RC6632.test()
    RC6M16.test()
    RC6M28.test()
    RC6M32.test()
    RC6M56.test()
    RCA.test()
    RCA38.test()
    RCA38Old.test()
    RCAOld.test()
    # RCMM.test()
    RECS800045.test()
    RECS800068.test()
    RECS800090.test()
    Revox.test()
    RTIRelay.test()
    Sampo.test()
    Samsung20.test()
    Samsung36.test()
    SamsungSMTG.test()
    ScAtl6.test()
    Sharp.test()
    Sharp1.test()
    Sharp2.test()
    SharpDVD.test()
    SIM2.test()
    Sky.test()
    SkyHD.test()
    SkyPlus.test()
    Somfy.test()
    Sony12.test()
    Sony15.test()
    Sony20.test()
    Sony8.test()
    Sunfire.test()
    TDC38.test()
    TDC56.test()
    TeacK.test()
    Thomson.test()
    # Velleman.test()
    Viewstar.test()
    # Whynter.test()
    Zaptor36.test()
    Zaptor56.test()
    XBox360.test()
    XBoxOne.test()
    Rs200.test()
    RC6MBIT.test()

    RC57F.enable(False)
    StreamZap.enable(True)
    StreamZap.test()

    RC57F57.enable(False)
    StreamZap57.enable(True)
    StreamZap57.test()

    Thomson.enable(False)
    Thomson7.enable(True)
    Thomson7.test()

    NEC.enable(False)
    NECrnc.enable(True)
    NECrnc.test()

    NEC.enable(False)
    NECf16.enable(False)
    Tivo.enable(True)
    Tivo.test()

    Blaupunkt.enable(True)
    Blaupunkt.test()

    Proton40.enable(False)
    Audiovox.enable(True)
    Audiovox.test()

    Roku.enable(True)
    Roku.test()

    if decoding_times:
        max_decode = max(decoding_times)
        avg_decode = sum(decoding_times) / float(len(decoding_times))
    else:
        max_decode = 0
        avg_decode = 0

    print('max decoding time:', max_decode, 'us (' + str(max_decode / 1000.0) + ' ms)')
    print('average decoding time:', avg_decode, 'us (' + str(avg_decode / 1000.0) + ' ms)')
    print('number of decodes:', len(decoding_times))
    print('total run time:', run_start.elapsed() / 1000.0, 'ms')

    print('failures:', len(failures))
    print('success:', len(success), success)
    print('skipped:', len(skipped), skipped)
    print('universals:', len(universals), universals)
    print('repeat_error:', len(repeat_error), repeat_error)
    print('decode_error:', len(decode_error), decode_error)
