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
from collections import deque

from .config import Config


class IRException(Exception):
    pass


class DecodeError(IRException):
    pass


class RepeatTimeoutExpired(IRException):
    pass


class RepeatLeadIn(IRException):
    pass


class RepeatLeadOut(IRException):
    pass


from .ad_notham import AdNotham  # NOQA
from .aiwa import Aiwa  # NOQA
from .akai import Akai  # NOQA
from .akord import Akord  # NOQA
from .amino import Amino  # NOQA
from .amino56 import Amino56  # NOQA
from .anthem import Anthem  # NOQA
from .apple import Apple  # NOQA
from .archer import Archer  # NOQA
from .arctech import Arctech  # NOQA
from .arctech38 import Arctech38  # NOQA
from .audiovox import Audiovox  # NOQA
from .barco import Barco  # NOQA
from .blaupunkt import Blaupunkt  # NOQA
from .bose import Bose  # NOQA
from .bryston import Bryston  # NOQA
from .canalsat import CanalSat  # NOQA
from .canalsatld import CanalSatLD  # NOQA
from .denon import Denon  # NOQA
from .denon1 import Denon1  # NOQA
from .denon2 import Denon2  # NOQA
from .denon_k import DenonK  # NOQA
from .dgtec import Dgtec  # NOQA
from .digivision import Digivision  # NOQA
from .directv import DirecTV  # NOQA
from .directv0 import DirecTV0  # NOQA
from .directv1 import DirecTV1  # NOQA
from .directv2 import DirecTV2  # NOQA
from .directv3 import DirecTV3  # NOQA
from .directv4 import DirecTV4  # NOQA
from .directv5 import DirecTV5  # NOQA
from .dishnetwork import DishNetwork  # NOQA
from .dishplayer import DishPlayer  # NOQA
from .dyson import Dyson  # NOQA
from .dyson2 import Dyson2  # NOQA
from .elan import Elan  # NOQA
from .elunevision import Elunevision  # NOQA
from .emerson import Emerson  # NOQA
from .entone import Entone  # NOQA
from .f12 import F12  # NOQA
from .f120 import F120  # NOQA
from .f121 import F121  # NOQA
from .f32 import F32  # NOQA
from .fujitsu import Fujitsu  # NOQA
from .fujitsu128 import Fujitsu128  # NOQA
from .fujitsu56 import Fujitsu56  # NOQA
from .gi4dtv import GI4DTV  # NOQA
from .gicable import GICable  # NOQA
from .girg import GIRG  # NOQA
from .grundig16 import Grundig16  # NOQA
from .grundig1630 import Grundig1630  # NOQA
from .guangzhou import GuangZhou  # NOQA
from .gwts import GwtS  # NOQA
from .gxb import GXB  # NOQA
from .humax4phase import Humax4Phase  # NOQA
from .intervideorc201 import InterVideoRC201  # NOQA
from .iodatan import IODATAn  # NOQA
from .jerrold import Jerrold  # NOQA
from .jvc import JVC  # NOQA
from .jvc48 import JVC48  # NOQA
from .jvc56 import JVC56  # NOQA
from .kaseikyo import Kaseikyo  # NOQA
from .kaseikyo56 import Kaseikyo56  # NOQA
from .kathrein import Kathrein  # NOQA
from .konka import Konka  # NOQA
from .logitech import Logitech  # NOQA
from .lumagen import Lumagen  # NOQA
from .lutron import Lutron  # NOQA
from .matsui import Matsui  # NOQA
from .mce import MCE  # NOQA
from .mcir2kbd import MCIR2kbd  # NOQA
from .mcir2mouse import MCIR2mouse  # NOQA
from .metz19 import Metz19  # NOQA
from .mitsubishi import Mitsubishi  # NOQA
from .mitsubishik import MitsubishiK  # NOQA
from .motorola import Motorola  # NOQA
from .nec import NEC  # NOQA
from .nec48 import NEC48  # NOQA
from .necf16 import NECf16  # NOQA
from .necrnc import NECrnc  # NOQA
from .necx import NECx  # NOQA
from .necxf16 import NECxf16  # NOQA
from .nokia import Nokia  # NOQA
from .nokia12 import Nokia12  # NOQA
from .nokia32 import Nokia32  # NOQA
from .novapace import NovaPace  # NOQA
from .nrc16 import NRC16  # NOQA
from .nrc1632 import NRC1632  # NOQA
from .nrc17 import NRC17  # NOQA
from .ortek import Ortek  # NOQA
from .ortekmce import OrtekMCE  # NOQA
from .pacemss import PaceMSS  # NOQA
from .panasonic import Panasonic  # NOQA
from .panasonic2 import Panasonic2  # NOQA
from .panasonicold import PanasonicOld  # NOQA
from .pctv import PCTV  # NOQA
from .pid0001 import PID0001  # NOQA
from .pid0003 import PID0003  # NOQA
from .pid0004 import PID0004  # NOQA
from .pid0083 import PID0083  # NOQA
from .pioneer import Pioneer  # NOQA
from .proton import Proton  # NOQA
from .proton40 import Proton40  # NOQA
from .rc5 import RC5  # NOQA
from .rc57f import RC57F  # NOQA
from .rc57f57 import RC57F57  # NOQA
from .rc5x import RC5x  # NOQA
from .rc6 import RC6  # NOQA
from .rc6620 import RC6620  # NOQA
from .rc6624 import RC6624  # NOQA
from .rc6632 import RC6632  # NOQA
from .rc6m16 import RC6M16  # NOQA
from .rc6m28 import RC6M28  # NOQA
from .rc6m32 import RC6M32  # NOQA
from .rc6m56 import RC6M56  # NOQA
from .rca import RCA  # NOQA
from .rca38 import RCA38  # NOQA
from .rca38old import RCA38Old  # NOQA
from .rcaold import RCAOld  # NOQA
from .rcmm import RCMM  # NOQA
from .recs800045 import RECS800045  # NOQA
from .recs800068 import RECS800068  # NOQA
from .recs800090 import RECS800090  # NOQA
from .revox import Revox  # NOQA
from .roku import Roku  # NOQA
from .rs200 import Rs200  # NOQA
from .rti_relay import RTIRelay  # NOQA
from .sampo import Sampo  # NOQA
from .samsung20 import Samsung20  # NOQA
from .samsung36 import Samsung36  # NOQA
from .samsungsmtg import SamsungSMTG  # NOQA
from .scatl6 import ScAtl6  # NOQA
from .sejin138 import Sejin138  # NOQA
from .sejin156 import Sejin156  # NOQA
from .sharp import Sharp  # NOQA
from .sharp1 import Sharp1  # NOQA
from .sharp2 import Sharp2  # NOQA
from .sharpdvd import SharpDVD  # NOQA
from .sim2 import SIM2  # NOQA
from .sky import Sky  # NOQA
from .sky_hd import SkyHD  # NOQA
from .sky_plus import SkyPlus  # NOQA
from .somfy import Somfy  # NOQA
from .sony12 import Sony12  # NOQA
from .sony15 import Sony15  # NOQA
from .sony20 import Sony20  # NOQA
from .sony8 import Sony8  # NOQA
# sonydsp
from .streamzap import StreamZap  # NOQA
from .streamzap57 import StreamZap57  # NOQA
from .sunfire import Sunfire  # NOQA
from .tdc38 import TDC38  # NOQA
from .tdc56 import TDC56  # NOQA
from .teack import TeacK  # NOQA
from .thomson import Thomson  # NOQA
from .thomson7 import Thomson7  # NOQA
from .tivo import Tivo  # NOQA
from .universal import Universal  # NOQA
# velleman
from .viewstar import Viewstar  # NOQA
# whynter
# x10
# x10n
# x10_18
# x10_8
from .xbox_360 import XBox360  # NOQA
from .xbox_one import XBoxOne  # NOQA
# zaptor36
# zaptor56

from . import protocol_base  # NOQA

_DECODERS = [
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
    Audiovox,
    Barco,
    Blaupunkt,
    Bose,
    Bryston,
    CanalSat,
    CanalSatLD,
    Denon,
    Denon1,
    Denon2,
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
    GI4DTV,
    GICable,
    GIRG,
    Grundig16,
    Grundig1630,
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
    NECrnc,
    NEC,
    NEC48,
    NECf16,
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
    Kaseikyo,
    Panasonic2,
    Kaseikyo56,
    PanasonicOld,
    PCTV,
    PID0001,
    PID0003,
    PID0004,
    PID0083,
    Pioneer,
    Proton,
    Proton40,
    RC5,
    RC6,
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
    Roku,
    RTIRelay,
    Sampo,
    Samsung20,
    Samsung36,
    SamsungSMTG,
    ScAtl6,
    Sejin138,
    Sejin156,
    Sharp,
    Sharp1,
    Sharp2,
    SharpDVD,
    SIM2,
    Sky,
    SkyHD,
    SkyPlus,
    RC6620,
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
    Thomson7,
    Tivo,
    Viewstar,
    XBox360,
    XBoxOne,
    NECx,
    NECxf16,
    RC5x,
    Rs200,
    RC57F,
    RC57F57,
    StreamZap,
    StreamZap57,
]


class IrDecoder(object):
    def __init__(self):
        self.__decoders = deque(_DECODERS[:])
        self.__last_decoder = None

    def __iter__(self):
        return iter(_DECODERS)

    @property
    def last_used_decoder(self):
        return self.__last_decoder

    def decode(self, data, frequency=0):
        if isinstance(data, protocol_base.IRCode):
            raise DecodeError('Input to be decoded must be RLC')

        if isinstance(data, tuple):
            data = list(data)

        if not isinstance(data, list):
            data = [[int(ord(x)) for x in data]]
        elif not isinstance(data[0], (list, tuple)):
            data = [[int(x) for x in data]]

        for i, rlc in enumerate(data):
            if len(rlc) < 3:
                if i + 1 < len(data):
                    data[i + 1] = rlc + data[i + 1]
                    continue
                return

        code = None

        for i, decoder in enumerate(self.__decoders):
            if not decoder.enabled:
                continue

            for rlc in data:
                try:
                    code = decoder.decode(rlc, frequency)
                except DecodeError:
                    break
                except (RepeatLeadIn, RepeatLeadOut, RepeatTimeoutExpired):
                    if len(data) == 1:
                        return None

                    continue

            else:
                self.__last_decoder = decoder
                break

        if code is None:
            code = self.Universal.decode(data[0], frequency)
            self.__last_decoder = self.Universal

        return code

    @property
    def enabled_decoders(self):
        res = []

        for decoder in self.__decoders:
            if decoder.enabled:
                res += [decoder.name]

        return res

    @property
    def disabled_decoders(self):
        res = []

        for decoder in self.__decoders:
            if not decoder.enabled:
                res += [decoder.name]

        return res

    @property
    def Universal(self):
        return Universal

    @property
    def AdNotham(self):
        return AdNotham

    @property
    def Aiwa(self):
        return Aiwa

    @property
    def Akai(self):
        return Akai

    @property
    def Akord(self):
        return Akord

    @property
    def Amino(self):
        return Amino

    @property
    def Amino56(self):
        return Amino56

    @property
    def Anthem(self):
        return Anthem

    @property
    def Apple(self):
        return Apple

    @property
    def Archer(self):
        return Archer

    @property
    def Arctech(self):
        return Arctech

    @property
    def Arctech38(self):
        return Arctech38

    @property
    def Audiovox(self):
        return Audiovox

    @property
    def Barco(self):
        return Barco

    @property
    def Blaupunkt(self):
        return Blaupunkt

    @property
    def Bose(self):
        return Bose

    @property
    def Bryston(self):
        return Bryston

    @property
    def CanalSat(self):
        return CanalSat

    @property
    def CanalSatLD(self):
        return CanalSatLD

    @property
    def Denon(self):
        return Denon

    @property
    def Denon1(self):
        return Denon1

    @property
    def Denon2(self):
        return Denon2

    @property
    def DenonK(self):
        return DenonK

    @property
    def Dgtec(self):
        return Dgtec

    @property
    def Digivision(self):
        return Digivision

    @property
    def DirecTV(self):
        return DirecTV

    @property
    def DishNetwork(self):
        return DishNetwork

    @property
    def DishPlayer(self):
        return DishPlayer

    @property
    def Dyson(self):
        return Dyson

    @property
    def Dyson2(self):
        return Dyson2

    @property
    def Elan(self):
        return Elan

    @property
    def Elunevision(self):
        return Elunevision

    @property
    def Emerson(self):
        return Emerson

    @property
    def Entone(self):
        return Entone

    @property
    def F12(self):
        return F12

    @property
    def F120(self):
        return F120

    @property
    def F121(self):
        return F121

    @property
    def F32(self):
        return F32

    @property
    def Fujitsu(self):
        return Fujitsu

    @property
    def Fujitsu128(self):
        return Fujitsu128

    @property
    def Fujitsu56(self):
        return Fujitsu56

    @property
    def GI4DTV(self):
        return GI4DTV

    @property
    def GICable(self):
        return GICable

    @property
    def GIRG(self):
        return GIRG

    @property
    def Grundig16(self):
        return Grundig16

    @property
    def Grundig1630(self):
        return Grundig1630

    @property
    def GuangZhou(self):
        return GuangZhou

    @property
    def GwtS(self):
        return GwtS

    @property
    def GXB(self):
        return GXB

    @property
    def Humax4Phase(self):
        return Humax4Phase

    @property
    def InterVideoRC201(self):
        return InterVideoRC201

    @property
    def IODATAn(self):
        return IODATAn

    @property
    def Jerrold(self):
        return Jerrold

    @property
    def JVC(self):
        return JVC

    @property
    def JVC48(self):
        return JVC48

    @property
    def JVC56(self):
        return JVC56

    @property
    def Kaseikyo(self):
        return Kaseikyo

    @property
    def Kaseikyo56(self):
        return Kaseikyo56

    @property
    def Kathrein(self):
        return Kathrein

    @property
    def Konka(self):
        return Konka

    @property
    def Logitech(self):
        return Logitech

    @property
    def Lumagen(self):
        return Lumagen

    @property
    def Lutron(self):
        return Lutron

    @property
    def Matsui(self):
        return Matsui

    @property
    def MCE(self):
        return MCE

    @property
    def MCIR2kbd(self):
        return MCIR2kbd

    @property
    def MCIR2mouse(self):
        return MCIR2mouse

    @property
    def Metz19(self):
        return Metz19

    @property
    def Mitsubishi(self):
        return Mitsubishi

    @property
    def MitsubishiK(self):
        return MitsubishiK

    @property
    def Motorola(self):
        return Motorola

    @property
    def NEC(self):
        return NEC

    @property
    def NEC48(self):
        return NEC48

    @property
    def NECf16(self):
        return NECf16

    @property
    def NECrnc(self):
        return NECrnc

    @property
    def NECx(self):
        return NECx

    @property
    def NECxf16(self):
        return NECxf16

    @property
    def Nokia(self):
        return Nokia

    @property
    def Nokia12(self):
        return Nokia12

    @property
    def Nokia32(self):
        return Nokia32

    @property
    def NovaPace(self):
        return NovaPace

    @property
    def NRC16(self):
        return NRC16

    @property
    def NRC1632(self):
        return NRC1632

    @property
    def NRC17(self):
        return NRC17

    @property
    def Ortek(self):
        return Ortek

    @property
    def OrtekMCE(self):
        return OrtekMCE

    @property
    def PaceMSS(self):
        return PaceMSS

    @property
    def Panasonic(self):
        return Panasonic

    @property
    def Panasonic2(self):
        return Panasonic2

    @property
    def PanasonicOld(self):
        return PanasonicOld

    @property
    def PCTV(self):
        return PCTV

    @property
    def PID0001(self):
        return PID0001

    @property
    def PID0003(self):
        return PID0003

    @property
    def PID0004(self):
        return PID0004

    @property
    def PID0083(self):
        return PID0083

    @property
    def Pioneer(self):
        return Pioneer

    @property
    def Proton(self):
        return Proton

    @property
    def Proton40(self):
        return Proton40

    @property
    def RC5(self):
        return RC5

    @property
    def RC57F(self):
        return RC57F

    @property
    def RC57F57(self):
        return RC57F57

    @property
    def RC5x(self):
        return RC5x

    @property
    def RC6(self):
        return RC6

    @property
    def RC6620(self):
        return RC6620

    @property
    def RC6624(self):
        return RC6624

    @property
    def RC6632(self):
        return RC6632

    @property
    def RC6M16(self):
        return RC6M16

    @property
    def RC6M28(self):
        return RC6M28

    @property
    def RC6M32(self):
        return RC6M32

    @property
    def RC6M56(self):
        return RC6M56

    @property
    def RCA(self):
        return RCA

    @property
    def RCA38(self):
        return RCA38

    @property
    def RCA38Old(self):
        return RCA38Old

    @property
    def RCAOld(self):
        return RCAOld

    @property
    def RCMM(self):
        return RCMM

    @property
    def RECS800045(self):
        return RECS800045

    @property
    def RECS800068(self):
        return RECS800068

    @property
    def RECS800090(self):
        return RECS800090

    @property
    def Revox(self):
        return Revox

    @property
    def Roku(self):
        return Roku

    @property
    def Rs200(self):
        return Rs200

    @property
    def RTIRelay(self):
        return RTIRelay

    @property
    def Sampo(self):
        return Sampo

    @property
    def Samsung20(self):
        return Samsung20

    @property
    def Samsung36(self):
        return Samsung36

    @property
    def SamsungSMTG(self):
        return SamsungSMTG

    @property
    def ScAtl6(self):
        return ScAtl6

    @property
    def Sejin138(self):
        return Sejin138

    @property
    def Sejin156(self):
        return Sejin156

    @property
    def Sharp(self):
        return Sharp

    @property
    def Sharp1(self):
        return Sharp1

    @property
    def Sharp2(self):
        return Sharp2

    @property
    def SharpDVD(self):
        return SharpDVD

    @property
    def SIM2(self):
        return SIM2

    @property
    def Sky(self):
        return Sky

    @property
    def SkyHD(self):
        return SkyHD

    @property
    def SkyPlus(self):
        return SkyPlus

    @property
    def Somfy(self):
        return Somfy

    @property
    def Sony12(self):
        return Sony12

    @property
    def Sony15(self):
        return Sony15

    @property
    def Sony20(self):
        return Sony20

    @property
    def Sony8(self):
        return Sony8

    @property
    def StreamZap(self):
        return StreamZap

    @property
    def StreamZap57(self):
        return StreamZap57

    @property
    def Sunfire(self):
        return Sunfire

    @property
    def TDC38(self):
        return TDC38

    @property
    def TDC56(self):
        return TDC56

    @property
    def TeacK(self):
        return TeacK

    @property
    def Thomson(self):
        return Thomson

    @property
    def Thomson7(self):
        return Thomson7

    @property
    def Tivo(self):
        return Tivo

    @property
    def Viewstar(self):
        return Viewstar

    @property
    def XBox360(self):
        return XBox360

    @property
    def XBoxOne(self):
        return XBoxOne


class IrEncoder(object):

    @property
    def AdNotham(self):
        return AdNotham

    @property
    def Aiwa(self):
        return Aiwa

    @property
    def Akai(self):
        return Akai

    @property
    def Akord(self):
        return Akord

    @property
    def Amino(self):
        return Amino

    @property
    def Amino56(self):
        return Amino56

    @property
    def Anthem(self):
        return Anthem

    @property
    def Apple(self):
        return Apple

    @property
    def Archer(self):
        return Archer

    @property
    def Arctech(self):
        return Arctech

    @property
    def Arctech38(self):
        return Arctech38

    @property
    def Audiovox(self):
        return Audiovox

    @property
    def Barco(self):
        return Barco

    @property
    def Blaupunkt(self):
        return Blaupunkt

    @property
    def Bose(self):
        return Bose

    @property
    def Bryston(self):
        return Bryston

    @property
    def CanalSat(self):
        return CanalSat

    @property
    def CanalSatLD(self):
        return CanalSatLD

    @property
    def Denon(self):
        return Denon

    @property
    def Denon1(self):
        return Denon1

    @property
    def Denon2(self):
        return Denon2

    @property
    def DenonK(self):
        return DenonK

    @property
    def Dgtec(self):
        return Dgtec

    @property
    def Digivision(self):
        return Digivision

    @property
    def DirecTV(self):
        return DirecTV

    @property
    def DishNetwork(self):
        return DishNetwork

    @property
    def DishPlayer(self):
        return DishPlayer

    @property
    def Dyson(self):
        return Dyson

    @property
    def Dyson2(self):
        return Dyson2

    @property
    def Elan(self):
        return Elan

    @property
    def Elunevision(self):
        return Elunevision

    @property
    def Emerson(self):
        return Emerson

    @property
    def Entone(self):
        return Entone

    @property
    def F12(self):
        return F12

    @property
    def F120(self):
        return F120

    @property
    def F121(self):
        return F121

    @property
    def F32(self):
        return F32

    @property
    def Fujitsu(self):
        return Fujitsu

    @property
    def Fujitsu128(self):
        return Fujitsu128

    @property
    def Fujitsu56(self):
        return Fujitsu56

    @property
    def GI4DTV(self):
        return GI4DTV

    @property
    def GICable(self):
        return GICable

    @property
    def GIRG(self):
        return GIRG

    @property
    def Grundig16(self):
        return Grundig16

    @property
    def Grundig1630(self):
        return Grundig1630

    @property
    def GuangZhou(self):
        return GuangZhou

    @property
    def GwtS(self):
        return GwtS

    @property
    def GXB(self):
        return GXB

    @property
    def Humax4Phase(self):
        return Humax4Phase

    @property
    def InterVideoRC201(self):
        return InterVideoRC201

    @property
    def IODATAn(self):
        return IODATAn

    @property
    def Jerrold(self):
        return Jerrold

    @property
    def JVC(self):
        return JVC

    @property
    def JVC48(self):
        return JVC48

    @property
    def JVC56(self):
        return JVC56

    @property
    def Kaseikyo(self):
        return Kaseikyo

    @property
    def Kaseikyo56(self):
        return Kaseikyo56

    @property
    def Kathrein(self):
        return Kathrein

    @property
    def Konka(self):
        return Konka

    @property
    def Logitech(self):
        return Logitech

    @property
    def Lumagen(self):
        return Lumagen

    @property
    def Lutron(self):
        return Lutron

    @property
    def Matsui(self):
        return Matsui

    @property
    def MCE(self):
        return MCE

    @property
    def MCIR2kbd(self):
        return MCIR2kbd

    @property
    def MCIR2mouse(self):
        return MCIR2mouse

    @property
    def Metz19(self):
        return Metz19

    @property
    def Mitsubishi(self):
        return Mitsubishi

    @property
    def MitsubishiK(self):
        return MitsubishiK

    @property
    def Motorola(self):
        return Motorola

    @property
    def NEC(self):
        return NEC

    @property
    def NEC48(self):
        return NEC48

    @property
    def NECf16(self):
        return NECf16

    @property
    def NECrnc(self):
        return NECrnc

    @property
    def NECx(self):
        return NECx

    @property
    def NECxf16(self):
        return NECxf16

    @property
    def Nokia(self):
        return Nokia

    @property
    def Nokia12(self):
        return Nokia12

    @property
    def Nokia32(self):
        return Nokia32

    @property
    def NovaPace(self):
        return NovaPace

    @property
    def NRC16(self):
        return NRC16

    @property
    def NRC1632(self):
        return NRC1632

    @property
    def NRC17(self):
        return NRC17

    @property
    def Ortek(self):
        return Ortek

    @property
    def OrtekMCE(self):
        return OrtekMCE

    @property
    def PaceMSS(self):
        return PaceMSS

    @property
    def Panasonic(self):
        return Panasonic

    @property
    def Panasonic2(self):
        return Panasonic2

    @property
    def PanasonicOld(self):
        return PanasonicOld

    @property
    def PCTV(self):
        return PCTV

    @property
    def PID0001(self):
        return PID0001

    @property
    def PID0003(self):
        return PID0003

    @property
    def PID0004(self):
        return PID0004

    @property
    def PID0083(self):
        return PID0083

    @property
    def Pioneer(self):
        return Pioneer

    @property
    def Proton(self):
        return Proton

    @property
    def Proton40(self):
        return Proton40

    @property
    def RC5(self):
        return RC5

    @property
    def RC57F(self):
        return RC57F

    @property
    def RC57F57(self):
        return RC57F57

    @property
    def RC5x(self):
        return RC5x

    @property
    def RC6(self):
        return RC6

    @property
    def RC6620(self):
        return RC6620

    @property
    def RC6624(self):
        return RC6624

    @property
    def RC6632(self):
        return RC6632

    @property
    def RC6M16(self):
        return RC6M16

    @property
    def RC6M28(self):
        return RC6M28

    @property
    def RC6M32(self):
        return RC6M32

    @property
    def RC6M56(self):
        return RC6M56

    @property
    def RCA(self):
        return RCA

    @property
    def RCA38(self):
        return RCA38

    @property
    def RCA38Old(self):
        return RCA38Old

    @property
    def RCAOld(self):
        return RCAOld

    @property
    def RCMM(self):
        return RCMM

    @property
    def RECS800045(self):
        return RECS800045

    @property
    def RECS800068(self):
        return RECS800068

    @property
    def RECS800090(self):
        return RECS800090

    @property
    def Revox(self):
        return Revox

    @property
    def Roku(self):
        return Roku

    @property
    def Rs200(self):
        return Rs200

    @property
    def RTIRelay(self):
        return RTIRelay

    @property
    def Sampo(self):
        return Sampo

    @property
    def Samsung20(self):
        return Samsung20

    @property
    def Samsung36(self):
        return Samsung36

    @property
    def SamsungSMTG(self):
        return SamsungSMTG

    @property
    def ScAtl6(self):
        return ScAtl6

    @property
    def Sejin138(self):
        return Sejin138

    @property
    def Sejin156(self):
        return Sejin156

    @property
    def Sharp(self):
        return Sharp

    @property
    def Sharp1(self):
        return Sharp1

    @property
    def Sharp2(self):
        return Sharp2

    @property
    def SharpDVD(self):
        return SharpDVD

    @property
    def SIM2(self):
        return SIM2

    @property
    def Sky(self):
        return Sky

    @property
    def SkyHD(self):
        return SkyHD

    @property
    def SkyPlus(self):
        return SkyPlus

    @property
    def Somfy(self):
        return Somfy

    @property
    def Sony12(self):
        return Sony12

    @property
    def Sony15(self):
        return Sony15

    @property
    def Sony20(self):
        return Sony20

    @property
    def Sony8(self):
        return Sony8

    @property
    def StreamZap(self):
        return StreamZap

    @property
    def StreamZap57(self):
        return StreamZap57

    @property
    def Sunfire(self):
        return Sunfire

    @property
    def TDC38(self):
        return TDC38

    @property
    def TDC56(self):
        return TDC56

    @property
    def TeacK(self):
        return TeacK

    @property
    def Thomson(self):
        return Thomson

    @property
    def Thomson7(self):
        return Thomson7

    @property
    def Tivo(self):
        return Tivo

    @property
    def Viewstar(self):
        return Viewstar

    @property
    def XBox360(self):
        return XBox360

    @property
    def XBoxOne(self):
        return XBoxOne


def decode_pronto_code(pronto_code):
    ir_decoder = IrDecoder()
    from . import pronto
    frequency, rlc = pronto.pronto_to_rlc(pronto_code)
    code = ir_decoder.decode(rlc, frequency)

    if code.decoder == ir_decoder.Universal:
        state = ir_decoder.RC57F.enabled
        ir_decoder.RC57F.enabled = False
        code = ir_decoder.decode(rlc, frequency)
        ir_decoder.RC57F.enabled = state

    if code.decoder == ir_decoder.Universal:
        state = ir_decoder.RC57F57.enabled
        ir_decoder.RC57F57.enabled = False
        code = ir_decoder.decode(rlc, frequency)
        ir_decoder.RC57F57.enabled = state

    if code.decoder == ir_decoder.Universal:
        state = ir_decoder.Thomson.enabled
        ir_decoder.Thomson.enabled = False
        code = ir_decoder.decode(rlc, frequency)
        ir_decoder.Thomson.enabled = state

    if code.decoder == ir_decoder.Universal:
        state1 = ir_decoder.NEC.enabled
        state2 = ir_decoder.NECf16.enabled
        ir_decoder.NEC.enabled = False
        ir_decoder.NECf16.enabled = False
        code = ir_decoder.decode(rlc, frequency)
        ir_decoder.NEC.enabled = state1
        ir_decoder.NECf16.enabled = state2

    return code


if __name__ == '__main__':
    import os
    import sys
    
    path = os.path.dirname(__file__)
    
    from . import protocol_base
    
    count = 0
    
    for f in os.listdir(path):
        if not f.endswith('py'):
            continue
            
        if f in (
            '__init__.py',
            'code_wrapper.py',
            'protocol_base.py', 
            'utils.py',
            'xml_handler.py',
            'config.py',
        ):
            continue
    
        mod_name = f.rsplit('.', 1)[0]
    
        try:
            __import__('decoders.' + mod_name)
        except AttributeError:
            continue
    
        mod = sys.modules['decoders.' + mod_name]
    
        for key, val in mod.__dict__.items():
            if key.startswith('_'):
                continue
    
            try:
                if isinstance(val, protocol_base.IrProtocolBase):
                    val._test_decode()
                    count += 1
    
                    break
            except TypeError:
                continue
    
    print('number of decoders:', count)
