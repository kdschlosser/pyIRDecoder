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
import random
import pyIRDecoder
import traceback
import threading
from pyIRDecoder import high_precision_timers, ExpectingMoreData


from pyIRDecoder import protocols

decoding_times = []

failures = []
skipped = []
universals = []
repeat_error = []
decode_error = []
success = []


last_code_data = None
last_code_frequency = None

class ExampleBase(object):
    encoder = None
    decoder = None

    @classmethod
    def is_enabled(cls):
        return cls.decoder.enabled

    @classmethod
    def enable(cls, value):
        cls.decoder.enabled = value

    @classmethod
    def test(cls):
        global last_code_data
        global last_code_frequency

        last_code_data = None
        last_code_frequency = None
        try:
            if not cls.is_enabled():
                print('skipping', cls.__name__)
                skipped.append(cls.__name__)
                return

            params = {}
            for name, min_val, max_val in cls.encoder.encode_parameters:
                val = random.randrange(min_val, max_val)
                params[name] = val

            print('encoding', cls.__name__)
            print('parameters:', params)

            start = high_precision_timers.TimerUS()
            rlc = cls.encoder.encode(**params)
            stop = start.elapsed()

            print('encoding duration:', stop, 'us')
            print('rlc:')
            print('[')
            for item in rlc:
                print('   ', str(item) + ',')
            print(']')
            print()

            repeat_count = random.randrange(1, 10)
            print('encoding', cls.__name__, '{0} repeats'.format(repeat_count))
            print('parameters:', params)

            start.reset()
            rlc = cls.encoder.encode(repeat_count=repeat_count, **params)
            stop = start.elapsed()
            last_code_data = [c for c in rlc]
            last_code_frequency = rlc.frequency

            print('encoding duration:', stop, 'us')
            print('rlc:')
            print('[')
            for item in rlc:
                print('   ', str(item) + ',')
            print(']')
            print()
            print()

            print('decoding', cls.__name__, '{0} repeats'.format(repeat_count))
            print('parameters:', params)
            print()
            wait_event = threading.Event()

            def key_released_callback(_):
                wait_event.set()

            code = None
            for c in rlc:
                if code is not None and not code.repeat_timer.is_running:
                    print('REPEAT CODE TIMER EXPIRED', code)

                start.reset()
                try:
                    c = protocols.decode(c, rlc.frequency)
                except ExpectingMoreData:
                    continue

                if c is None:
                    continue

                stop = start.elapsed()

                decoding_times.append(stop)
                print('decoding time:', stop, 'us')

                code = c
                code.bind_released_callback(key_released_callback)
                wait_event.wait(code.repeat_timer.duration / 1000000.0)
                print('setting timer duration:', code.repeat_timer.duration/1000000.0, 's')

            print()
            if code is None:
                for c in rlc:
                    c = cls.decoder.decode(c, rlc.frequency)
                    print(c)

                raise RuntimeError

            if code.decoder == protocols.Universal:
                universals.append(cls.__name__)
                raise RuntimeError

            if not isinstance(cls.decoder, code.decoder.__class__):
                raise RuntimeError(code.decoder.name + ' != ' + cls.decoder.name)

            wait_event.wait(10)

            print('decoded friendly:', code)
            print('decoded hexadecimal:', code.hexadecimal)
            print('code length:', code.repeat_timer.duration / 1000.0, 'ms')

            if not wait_event.is_set():
                repeat_error.append(cls.__name__)
                raise RuntimeError('repeat timeout problem')

            print()
            print('validating decode')
            print('parameter name      value      expected value')
            print('---------------------------------------------')
            for key, val in params.items():
                v = getattr(code, key.lower())
                print(key + ' ' * (20 - len(key)) + str(v) + ' ' * (11 - len(str(v))) + str(val))
                if v != val:
                    decode_error.append(cls.__name__)
                    raise ValueError(key + ', ' + str(val) + ', ' + str(v))

            print()
            print(code, 'successfully validated')
            print()
            print()
            success.append(cls.__name__)
        except:
            failures.append((cls.__name__, traceback.format_exc(), last_code_data, last_code_frequency))
            last_code_data = None
            last_code_frequency = None


class AdNotham(ExampleBase):
    decoder = protocols.AdNotham
    encoder = protocols.AdNotham


class Aiwa(ExampleBase):
    decoder = protocols.Aiwa
    encoder = protocols.Aiwa


class Akai(ExampleBase):
    decoder = protocols.Akai
    encoder = protocols.Akai


class Akord(ExampleBase):
    decoder = protocols.Akord
    encoder = protocols.Akord


class Amino(ExampleBase):
    decoder = protocols.Amino
    encoder = protocols.Amino


class Amino56(ExampleBase):
    decoder = protocols.Amino56
    encoder = protocols.Amino56


class Anthem(ExampleBase):
    decoder = protocols.Anthem
    encoder = protocols.Anthem


class Apple(ExampleBase):
    decoder = protocols.Apple
    encoder = protocols.Apple


class Archer(ExampleBase):
    decoder = protocols.Archer
    encoder = protocols.Archer


class Arctech(ExampleBase):
    decoder = protocols.Arctech
    encoder = protocols.Arctech


class Arctech38(ExampleBase):
    decoder = protocols.Arctech38
    encoder = protocols.Arctech38


class Audiovox(ExampleBase):
    decoder = protocols.Audiovox
    encoder = protocols.Audiovox


class Barco(ExampleBase):
    decoder = protocols.Barco
    encoder = protocols.Barco


class Blaupunkt(ExampleBase):
    decoder = protocols.Blaupunkt
    encoder = protocols.Blaupunkt


class Bose(ExampleBase):
    decoder = protocols.Bose
    encoder = protocols.Bose


class Bryston(ExampleBase):
    decoder = protocols.Bryston
    encoder = protocols.Bryston


class CanalSat(ExampleBase):
    decoder = protocols.CanalSat
    encoder = protocols.CanalSat


class CanalSatLD(ExampleBase):
    decoder = protocols.CanalSatLD
    encoder = protocols.CanalSatLD


class Denon(ExampleBase):
    decoder = protocols.Denon
    encoder = protocols.Denon


class DenonK(ExampleBase):
    decoder = protocols.DenonK
    encoder = protocols.DenonK


class Dgtec(ExampleBase):
    decoder = protocols.Dgtec
    encoder = protocols.Dgtec


class Digivision(ExampleBase):
    decoder = protocols.Digivision
    encoder = protocols.Digivision


class DirecTV(ExampleBase):
    decoder = protocols.DirecTV
    encoder = protocols.DirecTV


class DirecTV0(ExampleBase):
    decoder = protocols.DirecTV0
    encoder = protocols.DirecTV0


class DirecTV1(ExampleBase):
    decoder = protocols.DirecTV1
    encoder = protocols.DirecTV1


class DirecTV2(ExampleBase):
    decoder = protocols.DirecTV2
    encoder = protocols.DirecTV2


class DirecTV3(ExampleBase):
    decoder = protocols.DirecTV3
    encoder = protocols.DirecTV3


class DirecTV4(ExampleBase):
    decoder = protocols.DirecTV4
    encoder = protocols.DirecTV4


class DirecTV5(ExampleBase):
    decoder = protocols.DirecTV5
    encoder = protocols.DirecTV5


class DishNetwork(ExampleBase):
    decoder = protocols.DishNetwork
    encoder = protocols.DishNetwork


class DishPlayer(ExampleBase):
    decoder = protocols.DishPlayer
    encoder = protocols.DishPlayer


class Dyson(ExampleBase):
    decoder = protocols.Dyson
    encoder = protocols.Dyson


class Dyson2(ExampleBase):
    decoder = protocols.Dyson2
    encoder = protocols.Dyson2


class Elan(ExampleBase):
    decoder = protocols.Elan
    encoder = protocols.Elan


class Elunevision(ExampleBase):
    decoder = protocols.Elunevision
    encoder = protocols.Elunevision


class Emerson(ExampleBase):
    decoder = protocols.Emerson
    encoder = protocols.Emerson


class Entone(ExampleBase):
    decoder = protocols.Entone
    encoder = protocols.Entone


class F12(ExampleBase):
    decoder = protocols.F12
    encoder = protocols.F12


class F120(ExampleBase):
    decoder = protocols.F120
    encoder = protocols.F120


class F121(ExampleBase):
    decoder = protocols.F121
    encoder = protocols.F121


class F32(ExampleBase):
    decoder = protocols.F32
    encoder = protocols.F32


class Fujitsu(ExampleBase):
    decoder = protocols.Fujitsu
    encoder = protocols.Fujitsu


class Fujitsu128(ExampleBase):
    decoder = protocols.Fujitsu128
    encoder = protocols.Fujitsu128


class Fujitsu56(ExampleBase):
    decoder = protocols.Fujitsu56
    encoder = protocols.Fujitsu56


class GI4DTV(ExampleBase):
    decoder = protocols.GI4DTV
    encoder = protocols.GI4DTV


class GICable(ExampleBase):
    decoder = protocols.GICable
    encoder = protocols.GICable


class GIRG(ExampleBase):
    decoder = protocols.GIRG
    encoder = protocols.GIRG


class Grundig16(ExampleBase):
    decoder = protocols.Grundig16
    encoder = protocols.Grundig16


class Grundig1630(ExampleBase):
    decoder = protocols.Grundig1630
    encoder = protocols.Grundig1630


class GuangZhou(ExampleBase):
    decoder = protocols.GuangZhou
    encoder = protocols.GuangZhou


class GwtS(ExampleBase):
    decoder = protocols.GwtS
    encoder = protocols.GwtS


class GXB(ExampleBase):
    decoder = protocols.GXB
    encoder = protocols.GXB


class Humax4Phase(ExampleBase):
    decoder = protocols.Humax4Phase
    encoder = protocols.Humax4Phase


class InterVideoRC201(ExampleBase):
    decoder = protocols.InterVideoRC201
    encoder = protocols.InterVideoRC201


class IODATAn(ExampleBase):
    decoder = protocols.IODATAn
    encoder = protocols.IODATAn


class Jerrold(ExampleBase):
    decoder = protocols.Jerrold
    encoder = protocols.Jerrold


class JVC(ExampleBase):
    decoder = protocols.JVC
    encoder = protocols.JVC


class JVC48(ExampleBase):
    decoder = protocols.JVC48
    encoder = protocols.JVC48


class JVC56(ExampleBase):
    decoder = protocols.JVC56
    encoder = protocols.JVC56


class Kaseikyo(ExampleBase):
    decoder = protocols.Kaseikyo
    encoder = protocols.Kaseikyo


class Kaseikyo56(ExampleBase):
    decoder = protocols.Kaseikyo56
    encoder = protocols.Kaseikyo56


class Kathrein(ExampleBase):
    decoder = protocols.Kathrein
    encoder = protocols.Kathrein


class Konka(ExampleBase):
    decoder = protocols.Konka
    encoder = protocols.Konka


class Logitech(ExampleBase):
    decoder = protocols.Logitech
    encoder = protocols.Logitech


class Lumagen(ExampleBase):
    decoder = protocols.Lumagen
    encoder = protocols.Lumagen


class Lutron(ExampleBase):
    decoder = protocols.Lutron
    encoder = protocols.Lutron


class Matsui(ExampleBase):
    decoder = protocols.Matsui
    encoder = protocols.Matsui


class MCE(ExampleBase):
    decoder = protocols.MCE
    encoder = protocols.MCE


class MCIR2kbd(ExampleBase):
    decoder = protocols.MCIR2kbd
    encoder = protocols.MCIR2kbd


class MCIR2mouse(ExampleBase):
    decoder = protocols.MCIR2mouse
    encoder = protocols.MCIR2mouse


class Metz19(ExampleBase):
    decoder = protocols.Metz19
    encoder = protocols.Metz19


class Mitsubishi(ExampleBase):
    decoder = protocols.Mitsubishi
    encoder = protocols.Mitsubishi


class MitsubishiK(ExampleBase):
    decoder = protocols.MitsubishiK
    encoder = protocols.MitsubishiK


class Motorola(ExampleBase):
    decoder = protocols.Motorola
    encoder = protocols.Motorola


class NEC(ExampleBase):
    decoder = protocols.NEC
    encoder = protocols.NEC


class NEC48(ExampleBase):
    decoder = protocols.NEC48
    encoder = protocols.NEC48


class NECf16(ExampleBase):
    decoder = protocols.NECf16
    encoder = protocols.NECf16


class NECrnc(ExampleBase):
    decoder = protocols.NECrnc
    encoder = protocols.NECrnc


class NECx(ExampleBase):
    decoder = protocols.NECx
    encoder = protocols.NECx


class NECxf16(ExampleBase):
    decoder = protocols.NECxf16
    encoder = protocols.NECxf16


class NECYamaha(ExampleBase):
    decoder = protocols.NECYamaha
    encoder = protocols.NECYamaha


class Nokia(ExampleBase):
    decoder = protocols.Nokia
    encoder = protocols.Nokia


class Nokia12(ExampleBase):
    decoder = protocols.Nokia12
    encoder = protocols.Nokia12


class Nokia32(ExampleBase):
    decoder = protocols.Nokia32
    encoder = protocols.Nokia32


class NovaPace(ExampleBase):
    decoder = protocols.NovaPace
    encoder = protocols.NovaPace


class NRC16(ExampleBase):
    decoder = protocols.NRC16
    encoder = protocols.NRC16


class NRC1632(ExampleBase):
    decoder = protocols.NRC1632
    encoder = protocols.NRC1632


class NRC17(ExampleBase):
    decoder = protocols.NRC17
    encoder = protocols.NRC17


class Ortek(ExampleBase):
    decoder = protocols.Ortek
    encoder = protocols.Ortek


class OrtekMCE(ExampleBase):
    decoder = protocols.OrtekMCE
    encoder = protocols.OrtekMCE


class PaceMSS(ExampleBase):
    decoder = protocols.PaceMSS
    encoder = protocols.PaceMSS


class Panasonic(ExampleBase):
    decoder = protocols.Panasonic
    encoder = protocols.Panasonic


class Panasonic2(ExampleBase):
    decoder = protocols.Panasonic2
    encoder = protocols.Panasonic2


class PanasonicOld(ExampleBase):
    decoder = protocols.PanasonicOld
    encoder = protocols.PanasonicOld


class PCTV(ExampleBase):
    decoder = protocols.PCTV
    encoder = protocols.PCTV


class PID0001(ExampleBase):
    decoder = protocols.PID0001
    encoder = protocols.PID0001


class PID0003(ExampleBase):
    decoder = protocols.PID0003
    encoder = protocols.PID0003


class PID0004(ExampleBase):
    decoder = protocols.PID0004
    encoder = protocols.PID0004


class PID0083(ExampleBase):
    decoder = protocols.PID0083
    encoder = protocols.PID0083


class Pioneer(ExampleBase):
    decoder = protocols.Pioneer
    encoder = protocols.Pioneer


class Proton(ExampleBase):
    decoder = protocols.Proton
    encoder = protocols.Proton


class Proton40(ExampleBase):
    decoder = protocols.Proton40
    encoder = protocols.Proton40


class RC5(ExampleBase):
    decoder = protocols.RC5
    encoder = protocols.RC5


class RC57F(ExampleBase):
    decoder = protocols.RC57F
    encoder = protocols.RC57F


class RC57F57(ExampleBase):
    decoder = protocols.RC57F57
    encoder = protocols.RC57F57


class RC5x(ExampleBase):
    decoder = protocols.RC5x
    encoder = protocols.RC5x


class RC6(ExampleBase):
    decoder = protocols.RC6
    encoder = protocols.RC6


class RC6620(ExampleBase):
    decoder = protocols.RC6620
    encoder = protocols.RC6620


class RC6624(ExampleBase):
    decoder = protocols.RC6624
    encoder = protocols.RC6624


class RC6632(ExampleBase):
    decoder = protocols.RC6632
    encoder = protocols.RC6632


class RC6M16(ExampleBase):
    decoder = protocols.RC6M16
    encoder = protocols.RC6M16


class RC6M28(ExampleBase):
    decoder = protocols.RC6M28
    encoder = protocols.RC6M28


class RC6M32(ExampleBase):
    decoder = protocols.RC6M32
    encoder = protocols.RC6M32


class RC6M56(ExampleBase):
    decoder = protocols.RC6M56
    encoder = protocols.RC6M56


class RC6MBIT(ExampleBase):
    decoder = protocols.RC6MBIT
    encoder = protocols.RC6MBIT


class RCA(ExampleBase):
    decoder = protocols.RCA
    encoder = protocols.RCA


class RCA38(ExampleBase):
    decoder = protocols.RCA38
    encoder = protocols.RCA38


class RCA38Old(ExampleBase):
    decoder = protocols.RCA38Old
    encoder = protocols.RCA38Old


class RCAOld(ExampleBase):
    decoder = protocols.RCAOld
    encoder = protocols.RCAOld


#class RCMM(ExampleBase):
    #decoder = protocols.RCMM
    #encoder = protocols.RCMM


class RECS800045(ExampleBase):
    decoder = protocols.RECS800045
    encoder = protocols.RECS800045


class RECS800068(ExampleBase):
    decoder = protocols.RECS800068
    encoder = protocols.RECS800068


class RECS800090(ExampleBase):
    decoder = protocols.RECS800090
    encoder = protocols.RECS800090


class Revox(ExampleBase):
    decoder = protocols.Revox
    encoder = protocols.Revox


class Roku(ExampleBase):
    decoder = protocols.Roku
    encoder = protocols.Roku


class Rs200(ExampleBase):
    decoder = protocols.Rs200
    encoder = protocols.Rs200


class RTIRelay(ExampleBase):
    decoder = protocols.RTIRelay
    encoder = protocols.RTIRelay


class Sampo(ExampleBase):
    decoder = protocols.Sampo
    encoder = protocols.Sampo


class Samsung20(ExampleBase):
    decoder = protocols.Samsung20
    encoder = protocols.Samsung20


class Samsung36(ExampleBase):
    decoder = protocols.Samsung36
    encoder = protocols.Samsung36


class SamsungSMTG(ExampleBase):
    decoder = protocols.SamsungSMTG
    encoder = protocols.SamsungSMTG


class ScAtl6(ExampleBase):
    decoder = protocols.ScAtl6
    encoder = protocols.ScAtl6


class Sharp(ExampleBase):
    decoder = protocols.Sharp
    encoder = protocols.Sharp


class Sharp1(ExampleBase):
    decoder = protocols.Sharp1
    encoder = protocols.Sharp1


class Sharp2(ExampleBase):
    decoder = protocols.Sharp2
    encoder = protocols.Sharp2


class SharpDVD(ExampleBase):
    decoder = protocols.SharpDVD
    encoder = protocols.SharpDVD


class SIM2(ExampleBase):
    decoder = protocols.SIM2
    encoder = protocols.SIM2


class Sky(ExampleBase):
    decoder = protocols.Sky
    encoder = protocols.Sky


class SkyHD(ExampleBase):
    decoder = protocols.SkyHD
    encoder = protocols.SkyHD


class SkyPlus(ExampleBase):
    decoder = protocols.SkyPlus
    encoder = protocols.SkyPlus


class Somfy(ExampleBase):
    decoder = protocols.Somfy
    encoder = protocols.Somfy


class Sony12(ExampleBase):
    decoder = protocols.Sony12
    encoder = protocols.Sony12


class Sony15(ExampleBase):
    decoder = protocols.Sony15
    encoder = protocols.Sony15


class Sony20(ExampleBase):
    decoder = protocols.Sony20
    encoder = protocols.Sony20


class Sony8(ExampleBase):
    decoder = protocols.Sony8
    encoder = protocols.Sony8


class StreamZap(ExampleBase):
    decoder = protocols.StreamZap
    encoder = protocols.StreamZap


class StreamZap57(ExampleBase):
    decoder = protocols.StreamZap57
    encoder = protocols.StreamZap57


class Sunfire(ExampleBase):
    decoder = protocols.Sunfire
    encoder = protocols.Sunfire


class TDC38(ExampleBase):
    decoder = protocols.TDC38
    encoder = protocols.TDC38


class TDC56(ExampleBase):
    decoder = protocols.TDC56
    encoder = protocols.TDC56


class TeacK(ExampleBase):
    decoder = protocols.TeacK
    encoder = protocols.TeacK


class Thomson(ExampleBase):
    decoder = protocols.Thomson
    encoder = protocols.Thomson


class Thomson7(ExampleBase):
    decoder = protocols.Thomson7
    encoder = protocols.Thomson7


class Tivo(ExampleBase):
    decoder = protocols.Tivo
    encoder = protocols.Tivo


class Velleman(ExampleBase):
    decoder = protocols.Velleman
    encoder = protocols.Velleman


class Viewstar(ExampleBase):
    decoder = protocols.Viewstar
    encoder = protocols.Viewstar

#
# class Whynter(ExampleBase):
#     decoder = protocols.Whynter
#     encoder = protocols.Whynter
#

class Zaptor36(ExampleBase):
    decoder = protocols.Zaptor36
    encoder = protocols.Zaptor36


class Zaptor56(ExampleBase):
    decoder = protocols.Zaptor56
    encoder = protocols.Zaptor56


class XBox360(ExampleBase):
    decoder = protocols.XBox360
    encoder = protocols.XBox360


class XBoxOne(ExampleBase):
    decoder = protocols.XBoxOne
    encoder = protocols.XBoxOne

if __name__ == '__main__':
    protocols.Universal.enabled = False

    run_start = high_precision_timers.TimerUS()
    run_start.reset()
    classes = (
        AdNotham,
        Aiwa,
        Akai,
        Akord,
        Amino,
        Amino56,
        Anthem,
        Apple,
        Archer,
        Arctech,
        Arctech38,
        Barco,
        Bose,
        Bryston,
        CanalSat,
        CanalSatLD,
        Denon,
        DenonK,
        Dgtec,
        Digivision,
        DirecTV,
        DirecTV0,
        DirecTV1,
        DirecTV2,
        DirecTV3,
        DirecTV4,
        DirecTV5,
        DishNetwork,
        DishPlayer,
        Dyson,
        Dyson2,
        Elan,
        Elunevision,
        Emerson,
        Entone,
        F12,
        F120,
        F121,
        F32,
        Fujitsu,
        Fujitsu128,
        Fujitsu56,
        # GI4DTV,
        GICable,
        GIRG,
        # Grundig16,
        # Grundig1630,
        GuangZhou,
        GwtS,
        GXB,
        Humax4Phase,
        InterVideoRC201,
        IODATAn,
        Jerrold,
        JVC,
        JVC48,
        JVC56,
        Kaseikyo,
        Kaseikyo56,
        Kathrein,
        Konka,
        Logitech,
        Lumagen,
        Lutron,
        Matsui,
        MCE,
        MCIR2kbd,
        MCIR2mouse,
        Metz19,
        Mitsubishi,
        MitsubishiK,
        Motorola,
        NEC,
        NEC48,
        NECf16,
        NECx,
        NECxf16,
        NECYamaha,
        Nokia,
        Nokia12,
        Nokia32,
        NovaPace,
        NRC16,
        NRC1632,
        NRC17,
        Ortek,
        OrtekMCE,
        PaceMSS,
        Panasonic,
        Panasonic2,
        PanasonicOld,
        PCTV,
        PID0001,
        PID0003,
        PID0004,
        PID0083,
        Pioneer,
        Proton,
        RC5,
        RC57F,
        RC57F57,
        RC5x,
        RC6,
        RC6620,
        RC6624,
        RC6632,
        RC6M16,
        RC6M28,
        RC6M32,
        RC6M56,
        RCA,
        RCA38,
        RCA38Old,
        RCAOld,
        # RCMM,
        RECS800045,
        RECS800068,
        RECS800090,
        Revox,
        RTIRelay,
        Sampo,
        Samsung20,
        Samsung36,
        SamsungSMTG,
        ScAtl6,
        Sharp,
        Sharp1,
        Sharp2,
        SharpDVD,
        SIM2,
        Sky,
        SkyHD,
        SkyPlus,
        Somfy,
        Sony12,
        Sony15,
        Sony20,
        Sony8,
        Sunfire,
        TDC38,
        TDC56,
        TeacK,
        Thomson,
        # Velleman,
        Viewstar,
        # Whynter,
        Zaptor36,
        Zaptor56,
        Rs200,
        RC6MBIT
    )

    for cls in classes:
        try:
            cls.test()
        except:
            failures.append((cls.__name__, traceback.format_exc(), last_code_data, last_code_frequency))
            last_code_data = None
            last_code_frequency = None

    NECx.enable(False)
    NECxf16.enable(False)
    XBoxOne.test()

    RC6MBIT.enable(False)
    XBox360.test()

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
    NECf16.enable(False)
    NECYamaha.enable(False)
    NECrnc.enable(True)
    NECrnc.test()

    NEC.enable(False)
    NECf16.enable(False)
    Tivo.enable(True)
    Tivo.test()

    Blaupunkt.enable(True)
    Blaupunkt.test()

    Audiovox.enable(False)
    Proton40.test()

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

    print('success:', len(success), success)
    print('skipped:', len(skipped), skipped)
    print('universals:', len(universals), universals)
    print('repeat_error:', len(repeat_error), repeat_error)
    print('decode_error:', len(decode_error), decode_error)

    print()
    print()
    for name, tb, cd, cf in failures:
        print(name)
        print(cf)
        print(cd)
        print('*' * 20)
        print(tb)
        print()

    print()
    print('failures:', len(failures))
