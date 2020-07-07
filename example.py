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
import random
import pyIRDecoder
import time


ir_decoder = pyIRDecoder.IRDecoder()
ir_encoder = pyIRDecoder.IREncoder()

decoding_times = []


class TestBase(object):
    encoder = None
    decoder = None

    @classmethod
    def test(cls):
        print('encoding', cls.__name__)

        params = {}
        for name, min_val, max_val in cls.encoder.encode_parameters:

            if hasattr(cls.encoder, name):
                vals = getattr(cls.encoder, name)
                val = vals[random.randrange(0, len(vals) - 1)]
            else:
                val = random.randrange(min_val, max_val)

            params[name] = val

        print(params)
        start = time.time()

        rlc = cls.encoder.encode(**params)

        stop = time.time()
        print(rlc)
        print('encoding time:', (stop - start) * 1000, 'ms')
        print()

        print('decoding', cls.__name__)

        start = time.time()

        code = ir_decoder.decode(rlc, cls.decoder.frequency)

        print(cls.decoder, code.decoder.__class__)

        if code.decoder == ir_decoder.Universal:
            raise RuntimeError

        if not isinstance(cls.decoder, code.decoder.__class__):
            raise RuntimeError(code.decoder.name + ' != ' + cls.decoder.name)

        for key, val in params.items():
            v = getattr(code, key.lower())
            if v != val:
                raise ValueError(key + ', ' + str(val) + ', ' + str(v))

        print('success', code)
        print('decoded friendly', code)
        print('decoded hexdecimal', code.hexdecimal)

        stop = time.time()
        decoding_times.append((stop - start) * 1000)
        print('decoding time:', (stop - start) * 1000, 'ms')
        print()
        print()


class AdNotham(TestBase):
    decoder = ir_decoder.AdNotham
    encoder = ir_encoder.AdNotham


class Aiwa(TestBase):
    decoder = ir_decoder.Aiwa
    encoder = ir_encoder.Aiwa


class Akai(TestBase):
    decoder = ir_decoder.Akai
    encoder = ir_encoder.Akai


class Akord(TestBase):
    decoder = ir_decoder.Akord
    encoder = ir_encoder.Akord


class Amino(TestBase):
    decoder = ir_decoder.Amino
    encoder = ir_encoder.Amino


class Amino56(TestBase):
    decoder = ir_decoder.Amino56
    encoder = ir_encoder.Amino56


class Anthem(TestBase):
    decoder = ir_decoder.Anthem
    encoder = ir_encoder.Anthem


class Apple(TestBase):
    decoder = ir_decoder.Apple
    encoder = ir_encoder.Apple


class Archer(TestBase):
    decoder = ir_decoder.Archer
    encoder = ir_encoder.Archer


class Arctech(TestBase):
    decoder = ir_decoder.Arctech
    encoder = ir_encoder.Arctech


class Arctech38(TestBase):
    decoder = ir_decoder.Arctech38
    encoder = ir_encoder.Arctech38


class Audiovox(TestBase):
    decoder = ir_decoder.Audiovox
    encoder = ir_encoder.Audiovox


class Barco(TestBase):
    decoder = ir_decoder.Barco
    encoder = ir_encoder.Barco


class Blaupunkt(TestBase):
    decoder = ir_decoder.Blaupunkt
    encoder = ir_encoder.Blaupunkt


class Bose(TestBase):
    decoder = ir_decoder.Bose
    encoder = ir_encoder.Bose


class Bryston(TestBase):
    decoder = ir_decoder.Bryston
    encoder = ir_encoder.Bryston


class CanalSat(TestBase):
    decoder = ir_decoder.CanalSat
    encoder = ir_encoder.CanalSat


class CanalSatLD(TestBase):
    decoder = ir_decoder.CanalSatLD
    encoder = ir_encoder.CanalSatLD


class Denon(TestBase):
    decoder = ir_decoder.Denon
    encoder = ir_encoder.Denon


class Denon1(TestBase):
    decoder = ir_decoder.Denon1
    encoder = ir_encoder.Denon1


class Denon2(TestBase):
    decoder = ir_decoder.Denon2
    encoder = ir_encoder.Denon2


class DenonK(TestBase):
    decoder = ir_decoder.DenonK
    encoder = ir_encoder.DenonK


class Dgtec(TestBase):
    decoder = ir_decoder.Dgtec
    encoder = ir_encoder.Dgtec


class Digivision(TestBase):
    decoder = ir_decoder.Digivision
    encoder = ir_encoder.Digivision


class DirecTV(TestBase):
    decoder = ir_decoder.DirecTV
    encoder = ir_encoder.DirecTV


class DirecTV0(TestBase):
    decoder = ir_decoder.DirecTV0
    encoder = ir_encoder.DirecTV0


class DirecTV1(TestBase):
    decoder = ir_decoder.DirecTV1
    encoder = ir_encoder.DirecTV1


class DirecTV2(TestBase):
    decoder = ir_decoder.DirecTV2
    encoder = ir_encoder.DirecTV2


class DirecTV3(TestBase):
    decoder = ir_decoder.DirecTV3
    encoder = ir_encoder.DirecTV3


class DirecTV4(TestBase):
    decoder = ir_decoder.DirecTV4
    encoder = ir_encoder.DirecTV4


class DirecTV5(TestBase):
    decoder = ir_decoder.DirecTV5
    encoder = ir_encoder.DirecTV5


class DishNetwork(TestBase):
    decoder = ir_decoder.DishNetwork
    encoder = ir_encoder.DishNetwork


class DishPlayer(TestBase):
    decoder = ir_decoder.DishPlayer
    encoder = ir_encoder.DishPlayer


class Dyson(TestBase):
    decoder = ir_decoder.Dyson
    encoder = ir_encoder.Dyson


class Dyson2(TestBase):
    decoder = ir_decoder.Dyson2
    encoder = ir_encoder.Dyson2


class Elan(TestBase):
    decoder = ir_decoder.Elan
    encoder = ir_encoder.Elan


class Elunevision(TestBase):
    decoder = ir_decoder.Elunevision
    encoder = ir_encoder.Elunevision


class Emerson(TestBase):
    decoder = ir_decoder.Emerson
    encoder = ir_encoder.Emerson


class Entone(TestBase):
    decoder = ir_decoder.Entone
    encoder = ir_encoder.Entone


class F12(TestBase):
    decoder = ir_decoder.F12
    encoder = ir_encoder.F12


class F120(TestBase):
    decoder = ir_decoder.F120
    encoder = ir_encoder.F120


class F121(TestBase):
    decoder = ir_decoder.F121
    encoder = ir_encoder.F121


class F32(TestBase):
    decoder = ir_decoder.F32
    encoder = ir_encoder.F32


class Fujitsu(TestBase):
    decoder = ir_decoder.Fujitsu
    encoder = ir_encoder.Fujitsu


class Fujitsu128(TestBase):
    decoder = ir_decoder.Fujitsu128
    encoder = ir_encoder.Fujitsu128


class Fujitsu56(TestBase):
    decoder = ir_decoder.Fujitsu56
    encoder = ir_encoder.Fujitsu56


class GI4DTV(TestBase):
    decoder = ir_decoder.GI4DTV
    encoder = ir_encoder.GI4DTV


class GICable(TestBase):
    decoder = ir_decoder.GICable
    encoder = ir_encoder.GICable


class GIRG(TestBase):
    decoder = ir_decoder.GIRG
    encoder = ir_encoder.GIRG


class Grundig16(TestBase):
    decoder = ir_decoder.Grundig16
    encoder = ir_encoder.Grundig16


class Grundig1630(TestBase):
    decoder = ir_decoder.Grundig1630
    encoder = ir_encoder.Grundig1630


class GuangZhou(TestBase):
    decoder = ir_decoder.GuangZhou
    encoder = ir_encoder.GuangZhou


class GwtS(TestBase):
    decoder = ir_decoder.GwtS
    encoder = ir_encoder.GwtS


class GXB(TestBase):
    decoder = ir_decoder.GXB
    encoder = ir_encoder.GXB


class Humax4Phase(TestBase):
    decoder = ir_decoder.Humax4Phase
    encoder = ir_encoder.Humax4Phase


class InterVideoRC201(TestBase):
    decoder = ir_decoder.InterVideoRC201
    encoder = ir_encoder.InterVideoRC201


class IODATAn(TestBase):
    decoder = ir_decoder.IODATAn
    encoder = ir_encoder.IODATAn


class Jerrold(TestBase):
    decoder = ir_decoder.Jerrold
    encoder = ir_encoder.Jerrold


class JVC(TestBase):
    decoder = ir_decoder.JVC
    encoder = ir_encoder.JVC


class JVC48(TestBase):
    decoder = ir_decoder.JVC48
    encoder = ir_encoder.JVC48


class JVC56(TestBase):
    decoder = ir_decoder.JVC56
    encoder = ir_encoder.JVC56


class Kaseikyo(TestBase):
    decoder = ir_decoder.Kaseikyo
    encoder = ir_encoder.Kaseikyo


class Kaseikyo56(TestBase):
    decoder = ir_decoder.Kaseikyo56
    encoder = ir_encoder.Kaseikyo56


class Kathrein(TestBase):
    decoder = ir_decoder.Kathrein
    encoder = ir_encoder.Kathrein


class Konka(TestBase):
    decoder = ir_decoder.Konka
    encoder = ir_encoder.Konka


class Logitech(TestBase):
    decoder = ir_decoder.Logitech
    encoder = ir_encoder.Logitech


class Lumagen(TestBase):
    decoder = ir_decoder.Lumagen
    encoder = ir_encoder.Lumagen


class Lutron(TestBase):
    decoder = ir_decoder.Lutron
    encoder = ir_encoder.Lutron


class Matsui(TestBase):
    decoder = ir_decoder.Matsui
    encoder = ir_encoder.Matsui


class MCE(TestBase):
    decoder = ir_decoder.MCE
    encoder = ir_encoder.MCE


class MCIR2kbd(TestBase):
    decoder = ir_decoder.MCIR2kbd
    encoder = ir_encoder.MCIR2kbd


class MCIR2mouse(TestBase):
    decoder = ir_decoder.MCIR2mouse
    encoder = ir_encoder.MCIR2mouse


class Metz19(TestBase):
    decoder = ir_decoder.Metz19
    encoder = ir_encoder.Metz19


class Mitsubishi(TestBase):
    decoder = ir_decoder.Mitsubishi
    encoder = ir_encoder.Mitsubishi


class MitsubishiK(TestBase):
    decoder = ir_decoder.MitsubishiK
    encoder = ir_encoder.MitsubishiK


class Motorola(TestBase):
    decoder = ir_decoder.Motorola
    encoder = ir_encoder.Motorola


class NEC(TestBase):
    decoder = ir_decoder.NEC
    encoder = ir_encoder.NEC


class NEC48(TestBase):
    decoder = ir_decoder.NEC48
    encoder = ir_encoder.NEC48


class NECf16(TestBase):
    decoder = ir_decoder.NECf16
    encoder = ir_encoder.NECf16


class NECrnc(TestBase):
    decoder = ir_decoder.NECrnc
    encoder = ir_encoder.NECrnc


class NECx(TestBase):
    decoder = ir_decoder.NECx
    encoder = ir_encoder.NECx


class NECxf16(TestBase):
    decoder = ir_decoder.NECxf16
    encoder = ir_encoder.NECxf16


class Nokia(TestBase):
    decoder = ir_decoder.Nokia
    encoder = ir_encoder.Nokia


class Nokia12(TestBase):
    decoder = ir_decoder.Nokia12
    encoder = ir_encoder.Nokia12


class Nokia32(TestBase):
    decoder = ir_decoder.Nokia32
    encoder = ir_encoder.Nokia32


class NovaPace(TestBase):
    decoder = ir_decoder.NovaPace
    encoder = ir_encoder.NovaPace


class NRC16(TestBase):
    decoder = ir_decoder.NRC16
    encoder = ir_encoder.NRC16


class NRC1632(TestBase):
    decoder = ir_decoder.NRC1632
    encoder = ir_encoder.NRC1632


class NRC17(TestBase):
    decoder = ir_decoder.NRC17
    encoder = ir_encoder.NRC17


class Ortek(TestBase):
    decoder = ir_decoder.Ortek
    encoder = ir_encoder.Ortek


class OrtekMCE(TestBase):
    decoder = ir_decoder.OrtekMCE
    encoder = ir_encoder.OrtekMCE


class PaceMSS(TestBase):
    decoder = ir_decoder.PaceMSS
    encoder = ir_encoder.PaceMSS


class Panasonic(TestBase):
    decoder = ir_decoder.Panasonic
    encoder = ir_encoder.Panasonic


class Panasonic2(TestBase):
    decoder = ir_decoder.Panasonic2
    encoder = ir_encoder.Panasonic2


class PanasonicOld(TestBase):
    decoder = ir_decoder.PanasonicOld
    encoder = ir_encoder.PanasonicOld


class PCTV(TestBase):
    decoder = ir_decoder.PCTV
    encoder = ir_encoder.PCTV


class PID0001(TestBase):
    decoder = ir_decoder.PID0001
    encoder = ir_encoder.PID0001


class PID0003(TestBase):
    decoder = ir_decoder.PID0003
    encoder = ir_encoder.PID0003


class PID0004(TestBase):
    decoder = ir_decoder.PID0004
    encoder = ir_encoder.PID0004


class PID0083(TestBase):
    decoder = ir_decoder.PID0083
    encoder = ir_encoder.PID0083


class Pioneer(TestBase):
    decoder = ir_decoder.Pioneer
    encoder = ir_encoder.Pioneer


class Proton(TestBase):
    decoder = ir_decoder.Proton
    encoder = ir_encoder.Proton


class Proton40(TestBase):
    decoder = ir_decoder.Proton40
    encoder = ir_encoder.Proton40


class RC5(TestBase):
    decoder = ir_decoder.RC5
    encoder = ir_encoder.RC5


class RC57F(TestBase):
    decoder = ir_decoder.RC57F
    encoder = ir_encoder.RC57F


class RC57F57(TestBase):
    decoder = ir_decoder.RC57F57
    encoder = ir_encoder.RC57F57


class RC5x(TestBase):
    decoder = ir_decoder.RC5x
    encoder = ir_encoder.RC5x


class RC6(TestBase):
    decoder = ir_decoder.RC6
    encoder = ir_encoder.RC6


class RC6620(TestBase):
    decoder = ir_decoder.RC6620
    encoder = ir_encoder.RC6620


class RC6624(TestBase):
    decoder = ir_decoder.RC6624
    encoder = ir_encoder.RC6624


class RC6632(TestBase):
    decoder = ir_decoder.RC6632
    encoder = ir_encoder.RC6632


class RC6M16(TestBase):
    decoder = ir_decoder.RC6M16
    encoder = ir_encoder.RC6M16


class RC6M28(TestBase):
    decoder = ir_decoder.RC6M28
    encoder = ir_encoder.RC6M28


class RC6M32(TestBase):
    decoder = ir_decoder.RC6M32
    encoder = ir_encoder.RC6M32


class RC6M56(TestBase):
    decoder = ir_decoder.RC6M56
    encoder = ir_encoder.RC6M56


class RCA(TestBase):
    decoder = ir_decoder.RCA
    encoder = ir_encoder.RCA


class RCA38(TestBase):
    decoder = ir_decoder.RCA38
    encoder = ir_encoder.RCA38


class RCA38Old(TestBase):
    decoder = ir_decoder.RCA38Old
    encoder = ir_encoder.RCA38Old


class RCAOld(TestBase):
    decoder = ir_decoder.RCAOld
    encoder = ir_encoder.RCAOld


class RCMM(TestBase):
    decoder = ir_decoder.RCMM
    encoder = ir_encoder.RCMM


class RECS800045(TestBase):
    decoder = ir_decoder.RECS800045
    encoder = ir_encoder.RECS800045


class RECS800068(TestBase):
    decoder = ir_decoder.RECS800068
    encoder = ir_encoder.RECS800068


class RECS800090(TestBase):
    decoder = ir_decoder.RECS800090
    encoder = ir_encoder.RECS800090


class Revox(TestBase):
    decoder = ir_decoder.Revox
    encoder = ir_encoder.Revox


class Roku(TestBase):
    decoder = ir_decoder.Roku
    encoder = ir_encoder.Roku


class Rs200(TestBase):
    decoder = ir_decoder.Rs200
    encoder = ir_encoder.Rs200


class RTIRelay(TestBase):
    decoder = ir_decoder.RTIRelay
    encoder = ir_encoder.RTIRelay


class Sampo(TestBase):
    decoder = ir_decoder.Sampo
    encoder = ir_encoder.Sampo


class Samsung20(TestBase):
    decoder = ir_decoder.Samsung20
    encoder = ir_encoder.Samsung20


class Samsung36(TestBase):
    decoder = ir_decoder.Samsung36
    encoder = ir_encoder.Samsung36


class SamsungSMTG(TestBase):
    decoder = ir_decoder.SamsungSMTG
    encoder = ir_encoder.SamsungSMTG


class ScAtl6(TestBase):
    decoder = ir_decoder.ScAtl6
    encoder = ir_encoder.ScAtl6


class Sejin138(TestBase):
    decoder = ir_decoder.Sejin138
    encoder = ir_encoder.Sejin138


class Sejin156(TestBase):
    decoder = ir_decoder.Sejin156
    encoder = ir_encoder.Sejin156


class Sharp(TestBase):
    decoder = ir_decoder.Sharp
    encoder = ir_encoder.Sharp


class Sharp1(TestBase):
    decoder = ir_decoder.Sharp1
    encoder = ir_encoder.Sharp1


class Sharp2(TestBase):
    decoder = ir_decoder.Sharp2
    encoder = ir_encoder.Sharp2


class SharpDVD(TestBase):
    decoder = ir_decoder.SharpDVD
    encoder = ir_encoder.SharpDVD


class SIM2(TestBase):
    decoder = ir_decoder.SIM2
    encoder = ir_encoder.SIM2


class Sky(TestBase):
    decoder = ir_decoder.Sky
    encoder = ir_encoder.Sky


class SkyHD(TestBase):
    decoder = ir_decoder.SkyHD
    encoder = ir_encoder.SkyHD


class SkyPlus(TestBase):
    decoder = ir_decoder.SkyPlus
    encoder = ir_encoder.SkyPlus


class Somfy(TestBase):
    decoder = ir_decoder.Somfy
    encoder = ir_encoder.Somfy


class Sony12(TestBase):
    decoder = ir_decoder.Sony12
    encoder = ir_encoder.Sony12


class Sony15(TestBase):
    decoder = ir_decoder.Sony15
    encoder = ir_encoder.Sony15


class Sony20(TestBase):
    decoder = ir_decoder.Sony20
    encoder = ir_encoder.Sony20


class Sony8(TestBase):
    decoder = ir_decoder.Sony8
    encoder = ir_encoder.Sony8


class StreamZap(TestBase):
    decoder = ir_decoder.StreamZap
    encoder = ir_encoder.StreamZap


class StreamZap57(TestBase):
    decoder = ir_decoder.StreamZap57
    encoder = ir_encoder.StreamZap57


class Sunfire(TestBase):
    decoder = ir_decoder.Sunfire
    encoder = ir_encoder.Sunfire


class TDC38(TestBase):
    decoder = ir_decoder.TDC38
    encoder = ir_encoder.TDC38


class TDC56(TestBase):
    decoder = ir_decoder.TDC56
    encoder = ir_encoder.TDC56


class TeacK(TestBase):
    decoder = ir_decoder.TeacK
    encoder = ir_encoder.TeacK


class Thomson(TestBase):
    decoder = ir_decoder.Thomson
    encoder = ir_encoder.Thomson


class Thomson7(TestBase):
    decoder = ir_decoder.Thomson7
    encoder = ir_encoder.Thomson7


class Tivo(TestBase):
    decoder = ir_decoder.Tivo
    encoder = ir_encoder.Tivo


class Viewstar(TestBase):
    decoder = ir_decoder.Viewstar
    encoder = ir_encoder.Viewstar


class XBox360(TestBase):
    decoder = ir_decoder.XBox360
    encoder = ir_encoder.XBox360


class XBoxOne(TestBase):
    decoder = ir_decoder.XBoxOne
    encoder = ir_encoder.XBoxOne


if __name__ == '__main__':
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
    Audiovox.test()
    Barco.test()
    Blaupunkt.test()
    Bose.test()
    Bryston.test()
    CanalSat.test()
    CanalSatLD.test()
    Denon2.test()
    Denon.test()
    Denon1.test()
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
    NECrnc.test()
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
    Roku.test()
    RTIRelay.test()
    Sampo.test()
    Samsung20.test()
    Samsung36.test()
    SamsungSMTG.test()
    ScAtl6.test()
    # Sejin138.test()
    # Sejin156.test()
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
    Viewstar.test()
    XBox360.test()
    XBoxOne.test()
    # Rs200.test()

    ir_decoder.RC57F.enabled = False
    StreamZap.test()

    ir_decoder.RC57F57.enabled = False
    StreamZap57.test()

    ir_decoder.Thomson.enabled = False
    Thomson7.test()

    ir_decoder.NEC.enabled = False
    ir_decoder.NECf16.enabled = False
    Tivo.test()

    print('average decoding time:', sum(decoding_times) / float(len(decoding_times)), 'ms')
