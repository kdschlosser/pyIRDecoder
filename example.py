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
from pyIRDecoder import high_precision_timers


from pyIRDecoder import protocols

decoding_times = []

failures = []
skipped = []
universals = []
repeat_error = []
decode_error = []
success = []


class TestBase(object):
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
        try:
            if not cls.is_enabled():
                print('skipping', cls.__name__)
                skipped.append(cls.__name__)
                return

            params = {}
            for name, min_val, max_val in cls.encoder.encode_parameters:

                if hasattr(cls.encoder, name):
                    vals = getattr(cls.encoder, name)
                    val = vals[random.randrange(0, len(vals) - 1)]
                else:
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
                c = protocols.decode(c, rlc.frequency)

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

                failures.append(cls.__name__)
                raise RuntimeError

            if code.decoder == protocols.Universal:
                universals.append(cls.__name__)
                raise RuntimeError

            if not isinstance(cls.decoder, code.decoder.__class__):
                raise RuntimeError(code.decoder.name + ' != ' + cls.decoder.name)

            wait_event.wait(10)

            print('key released')
            print()
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
            failures.append(cls.__name__)
            print()
            traceback.print_exc()
            print()
            print()


class AdNotham(TestBase):
    decoder = protocols.AdNotham
    encoder = protocols.AdNotham


class Aiwa(TestBase):
    decoder = protocols.Aiwa
    encoder = protocols.Aiwa


class Akai(TestBase):
    decoder = protocols.Akai
    encoder = protocols.Akai


class Akord(TestBase):
    decoder = protocols.Akord
    encoder = protocols.Akord


class Amino(TestBase):
    decoder = protocols.Amino
    encoder = protocols.Amino


class Amino56(TestBase):
    decoder = protocols.Amino56
    encoder = protocols.Amino56


class Anthem(TestBase):
    decoder = protocols.Anthem
    encoder = protocols.Anthem


class Apple(TestBase):
    decoder = protocols.Apple
    encoder = protocols.Apple


class Archer(TestBase):
    decoder = protocols.Archer
    encoder = protocols.Archer


class Arctech(TestBase):
    decoder = protocols.Arctech
    encoder = protocols.Arctech


class Arctech38(TestBase):
    decoder = protocols.Arctech38
    encoder = protocols.Arctech38


class Audiovox(TestBase):
    decoder = protocols.Audiovox
    encoder = protocols.Audiovox


class Barco(TestBase):
    decoder = protocols.Barco
    encoder = protocols.Barco


class Blaupunkt(TestBase):
    decoder = protocols.Blaupunkt
    encoder = protocols.Blaupunkt


class Bose(TestBase):
    decoder = protocols.Bose
    encoder = protocols.Bose


class Bryston(TestBase):
    decoder = protocols.Bryston
    encoder = protocols.Bryston


class CanalSat(TestBase):
    decoder = protocols.CanalSat
    encoder = protocols.CanalSat


class CanalSatLD(TestBase):
    decoder = protocols.CanalSatLD
    encoder = protocols.CanalSatLD


class Denon(TestBase):
    decoder = protocols.Denon
    encoder = protocols.Denon


class DenonK(TestBase):
    decoder = protocols.DenonK
    encoder = protocols.DenonK


class Dgtec(TestBase):
    decoder = protocols.Dgtec
    encoder = protocols.Dgtec


class Digivision(TestBase):
    decoder = protocols.Digivision
    encoder = protocols.Digivision


class DirecTV(TestBase):
    decoder = protocols.DirecTV
    encoder = protocols.DirecTV


class DirecTV0(TestBase):
    decoder = protocols.DirecTV0
    encoder = protocols.DirecTV0


class DirecTV1(TestBase):
    decoder = protocols.DirecTV1
    encoder = protocols.DirecTV1


class DirecTV2(TestBase):
    decoder = protocols.DirecTV2
    encoder = protocols.DirecTV2


class DirecTV3(TestBase):
    decoder = protocols.DirecTV3
    encoder = protocols.DirecTV3


class DirecTV4(TestBase):
    decoder = protocols.DirecTV4
    encoder = protocols.DirecTV4


class DirecTV5(TestBase):
    decoder = protocols.DirecTV5
    encoder = protocols.DirecTV5


class DishNetwork(TestBase):
    decoder = protocols.DishNetwork
    encoder = protocols.DishNetwork


class DishPlayer(TestBase):
    decoder = protocols.DishPlayer
    encoder = protocols.DishPlayer


class Dyson(TestBase):
    decoder = protocols.Dyson
    encoder = protocols.Dyson


class Dyson2(TestBase):
    decoder = protocols.Dyson2
    encoder = protocols.Dyson2


class Elan(TestBase):
    decoder = protocols.Elan
    encoder = protocols.Elan


class Elunevision(TestBase):
    decoder = protocols.Elunevision
    encoder = protocols.Elunevision


class Emerson(TestBase):
    decoder = protocols.Emerson
    encoder = protocols.Emerson


class Entone(TestBase):
    decoder = protocols.Entone
    encoder = protocols.Entone


class F12(TestBase):
    decoder = protocols.F12
    encoder = protocols.F12


class F120(TestBase):
    decoder = protocols.F120
    encoder = protocols.F120


class F121(TestBase):
    decoder = protocols.F121
    encoder = protocols.F121


class F32(TestBase):
    decoder = protocols.F32
    encoder = protocols.F32


class Fujitsu(TestBase):
    decoder = protocols.Fujitsu
    encoder = protocols.Fujitsu


class Fujitsu128(TestBase):
    decoder = protocols.Fujitsu128
    encoder = protocols.Fujitsu128


class Fujitsu56(TestBase):
    decoder = protocols.Fujitsu56
    encoder = protocols.Fujitsu56


class GI4DTV(TestBase):
    decoder = protocols.GI4DTV
    encoder = protocols.GI4DTV


class GICable(TestBase):
    decoder = protocols.GICable
    encoder = protocols.GICable


class GIRG(TestBase):
    decoder = protocols.GIRG
    encoder = protocols.GIRG


class Grundig16(TestBase):
    decoder = protocols.Grundig16
    encoder = protocols.Grundig16


class Grundig1630(TestBase):
    decoder = protocols.Grundig1630
    encoder = protocols.Grundig1630


class GuangZhou(TestBase):
    decoder = protocols.GuangZhou
    encoder = protocols.GuangZhou


class GwtS(TestBase):
    decoder = protocols.GwtS
    encoder = protocols.GwtS


class GXB(TestBase):
    decoder = protocols.GXB
    encoder = protocols.GXB


class Humax4Phase(TestBase):
    decoder = protocols.Humax4Phase
    encoder = protocols.Humax4Phase


class InterVideoRC201(TestBase):
    decoder = protocols.InterVideoRC201
    encoder = protocols.InterVideoRC201


class IODATAn(TestBase):
    decoder = protocols.IODATAn
    encoder = protocols.IODATAn


class Jerrold(TestBase):
    decoder = protocols.Jerrold
    encoder = protocols.Jerrold


class JVC(TestBase):
    decoder = protocols.JVC
    encoder = protocols.JVC


class JVC48(TestBase):
    decoder = protocols.JVC48
    encoder = protocols.JVC48


class JVC56(TestBase):
    decoder = protocols.JVC56
    encoder = protocols.JVC56


class Kaseikyo(TestBase):
    decoder = protocols.Kaseikyo
    encoder = protocols.Kaseikyo


class Kaseikyo56(TestBase):
    decoder = protocols.Kaseikyo56
    encoder = protocols.Kaseikyo56


class Kathrein(TestBase):
    decoder = protocols.Kathrein
    encoder = protocols.Kathrein


class Konka(TestBase):
    decoder = protocols.Konka
    encoder = protocols.Konka


class Logitech(TestBase):
    decoder = protocols.Logitech
    encoder = protocols.Logitech


class Lumagen(TestBase):
    decoder = protocols.Lumagen
    encoder = protocols.Lumagen


class Lutron(TestBase):
    decoder = protocols.Lutron
    encoder = protocols.Lutron


class Matsui(TestBase):
    decoder = protocols.Matsui
    encoder = protocols.Matsui


class MCE(TestBase):
    decoder = protocols.MCE
    encoder = protocols.MCE


class MCIR2kbd(TestBase):
    decoder = protocols.MCIR2kbd
    encoder = protocols.MCIR2kbd


class MCIR2mouse(TestBase):
    decoder = protocols.MCIR2mouse
    encoder = protocols.MCIR2mouse


class Metz19(TestBase):
    decoder = protocols.Metz19
    encoder = protocols.Metz19


class Mitsubishi(TestBase):
    decoder = protocols.Mitsubishi
    encoder = protocols.Mitsubishi


class MitsubishiK(TestBase):
    decoder = protocols.MitsubishiK
    encoder = protocols.MitsubishiK


class Motorola(TestBase):
    decoder = protocols.Motorola
    encoder = protocols.Motorola


class NEC(TestBase):
    decoder = protocols.NEC
    encoder = protocols.NEC


class NEC48(TestBase):
    decoder = protocols.NEC48
    encoder = protocols.NEC48


class NECf16(TestBase):
    decoder = protocols.NECf16
    encoder = protocols.NECf16


class NECrnc(TestBase):
    decoder = protocols.NECrnc
    encoder = protocols.NECrnc


class NECx(TestBase):
    decoder = protocols.NECx
    encoder = protocols.NECx


class NECxf16(TestBase):
    decoder = protocols.NECxf16
    encoder = protocols.NECxf16


class Nokia(TestBase):
    decoder = protocols.Nokia
    encoder = protocols.Nokia


class Nokia12(TestBase):
    decoder = protocols.Nokia12
    encoder = protocols.Nokia12


class Nokia32(TestBase):
    decoder = protocols.Nokia32
    encoder = protocols.Nokia32


class NovaPace(TestBase):
    decoder = protocols.NovaPace
    encoder = protocols.NovaPace


class NRC16(TestBase):
    decoder = protocols.NRC16
    encoder = protocols.NRC16


class NRC1632(TestBase):
    decoder = protocols.NRC1632
    encoder = protocols.NRC1632


class NRC17(TestBase):
    decoder = protocols.NRC17
    encoder = protocols.NRC17


class Ortek(TestBase):
    decoder = protocols.Ortek
    encoder = protocols.Ortek


class OrtekMCE(TestBase):
    decoder = protocols.OrtekMCE
    encoder = protocols.OrtekMCE


class PaceMSS(TestBase):
    decoder = protocols.PaceMSS
    encoder = protocols.PaceMSS


class Panasonic(TestBase):
    decoder = protocols.Panasonic
    encoder = protocols.Panasonic


class Panasonic2(TestBase):
    decoder = protocols.Panasonic2
    encoder = protocols.Panasonic2


class PanasonicOld(TestBase):
    decoder = protocols.PanasonicOld
    encoder = protocols.PanasonicOld


class PCTV(TestBase):
    decoder = protocols.PCTV
    encoder = protocols.PCTV


class PID0001(TestBase):
    decoder = protocols.PID0001
    encoder = protocols.PID0001


class PID0003(TestBase):
    decoder = protocols.PID0003
    encoder = protocols.PID0003


class PID0004(TestBase):
    decoder = protocols.PID0004
    encoder = protocols.PID0004


class PID0083(TestBase):
    decoder = protocols.PID0083
    encoder = protocols.PID0083


class Pioneer(TestBase):
    decoder = protocols.Pioneer
    encoder = protocols.Pioneer


class Proton(TestBase):
    decoder = protocols.Proton
    encoder = protocols.Proton


class Proton40(TestBase):
    decoder = protocols.Proton40
    encoder = protocols.Proton40


class RC5(TestBase):
    decoder = protocols.RC5
    encoder = protocols.RC5


class RC57F(TestBase):
    decoder = protocols.RC57F
    encoder = protocols.RC57F


class RC57F57(TestBase):
    decoder = protocols.RC57F57
    encoder = protocols.RC57F57


class RC5x(TestBase):
    decoder = protocols.RC5x
    encoder = protocols.RC5x


class RC6(TestBase):
    decoder = protocols.RC6
    encoder = protocols.RC6


class RC6620(TestBase):
    decoder = protocols.RC6620
    encoder = protocols.RC6620


class RC6624(TestBase):
    decoder = protocols.RC6624
    encoder = protocols.RC6624


class RC6632(TestBase):
    decoder = protocols.RC6632
    encoder = protocols.RC6632


class RC6M16(TestBase):
    decoder = protocols.RC6M16
    encoder = protocols.RC6M16


class RC6M28(TestBase):
    decoder = protocols.RC6M28
    encoder = protocols.RC6M28


class RC6M32(TestBase):
    decoder = protocols.RC6M32
    encoder = protocols.RC6M32


class RC6M56(TestBase):
    decoder = protocols.RC6M56
    encoder = protocols.RC6M56


class RC6MBIT(TestBase):
    decoder = protocols.RC6MBIT
    encoder = protocols.RC6MBIT


class RCA(TestBase):
    decoder = protocols.RCA
    encoder = protocols.RCA


class RCA38(TestBase):
    decoder = protocols.RCA38
    encoder = protocols.RCA38


class RCA38Old(TestBase):
    decoder = protocols.RCA38Old
    encoder = protocols.RCA38Old


class RCAOld(TestBase):
    decoder = protocols.RCAOld
    encoder = protocols.RCAOld


#class RCMM(TestBase):
    #decoder = protocols.RCMM
    #encoder = protocols.RCMM


class RECS800045(TestBase):
    decoder = protocols.RECS800045
    encoder = protocols.RECS800045


class RECS800068(TestBase):
    decoder = protocols.RECS800068
    encoder = protocols.RECS800068


class RECS800090(TestBase):
    decoder = protocols.RECS800090
    encoder = protocols.RECS800090


class Revox(TestBase):
    decoder = protocols.Revox
    encoder = protocols.Revox


class Roku(TestBase):
    decoder = protocols.Roku
    encoder = protocols.Roku


class Rs200(TestBase):
    decoder = protocols.Rs200
    encoder = protocols.Rs200


class RTIRelay(TestBase):
    decoder = protocols.RTIRelay
    encoder = protocols.RTIRelay


class Sampo(TestBase):
    decoder = protocols.Sampo
    encoder = protocols.Sampo


class Samsung20(TestBase):
    decoder = protocols.Samsung20
    encoder = protocols.Samsung20


class Samsung36(TestBase):
    decoder = protocols.Samsung36
    encoder = protocols.Samsung36


class SamsungSMTG(TestBase):
    decoder = protocols.SamsungSMTG
    encoder = protocols.SamsungSMTG


class ScAtl6(TestBase):
    decoder = protocols.ScAtl6
    encoder = protocols.ScAtl6


class Sharp(TestBase):
    decoder = protocols.Sharp
    encoder = protocols.Sharp


class Sharp1(TestBase):
    decoder = protocols.Sharp1
    encoder = protocols.Sharp1


class Sharp2(TestBase):
    decoder = protocols.Sharp2
    encoder = protocols.Sharp2


class SharpDVD(TestBase):
    decoder = protocols.SharpDVD
    encoder = protocols.SharpDVD


class SIM2(TestBase):
    decoder = protocols.SIM2
    encoder = protocols.SIM2


class Sky(TestBase):
    decoder = protocols.Sky
    encoder = protocols.Sky


class SkyHD(TestBase):
    decoder = protocols.SkyHD
    encoder = protocols.SkyHD


class SkyPlus(TestBase):
    decoder = protocols.SkyPlus
    encoder = protocols.SkyPlus


class Somfy(TestBase):
    decoder = protocols.Somfy
    encoder = protocols.Somfy


class Sony12(TestBase):
    decoder = protocols.Sony12
    encoder = protocols.Sony12


class Sony15(TestBase):
    decoder = protocols.Sony15
    encoder = protocols.Sony15


class Sony20(TestBase):
    decoder = protocols.Sony20
    encoder = protocols.Sony20


class Sony8(TestBase):
    decoder = protocols.Sony8
    encoder = protocols.Sony8


class StreamZap(TestBase):
    decoder = protocols.StreamZap
    encoder = protocols.StreamZap


class StreamZap57(TestBase):
    decoder = protocols.StreamZap57
    encoder = protocols.StreamZap57


class Sunfire(TestBase):
    decoder = protocols.Sunfire
    encoder = protocols.Sunfire


class TDC38(TestBase):
    decoder = protocols.TDC38
    encoder = protocols.TDC38


class TDC56(TestBase):
    decoder = protocols.TDC56
    encoder = protocols.TDC56


class TeacK(TestBase):
    decoder = protocols.TeacK
    encoder = protocols.TeacK


class Thomson(TestBase):
    decoder = protocols.Thomson
    encoder = protocols.Thomson


class Thomson7(TestBase):
    decoder = protocols.Thomson7
    encoder = protocols.Thomson7


class Tivo(TestBase):
    decoder = protocols.Tivo
    encoder = protocols.Tivo


class Velleman(TestBase):
    decoder = protocols.Velleman
    encoder = protocols.Velleman


class Viewstar(TestBase):
    decoder = protocols.Viewstar
    encoder = protocols.Viewstar

#
# class Whynter(TestBase):
#     decoder = protocols.Whynter
#     encoder = protocols.Whynter
#

class Zaptor36(TestBase):
    decoder = protocols.Zaptor36
    encoder = protocols.Zaptor36


class Zaptor56(TestBase):
    decoder = protocols.Zaptor56
    encoder = protocols.Zaptor56


class XBox360(TestBase):
    decoder = protocols.XBox360
    encoder = protocols.XBox360


class XBoxOne(TestBase):
    decoder = protocols.XBoxOne
    encoder = protocols.XBoxOne

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

    print('failures:', len(failures), failures)
    print('success:', len(success), success)
    print('skipped:', len(skipped), skipped)
    print('universals:', len(universals), universals)
    print('repeat_error:', len(repeat_error), repeat_error)
    print('decode_error:', len(decode_error), decode_error)
