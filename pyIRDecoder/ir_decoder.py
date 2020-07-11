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


from collections import deque
from . import (
    DecodeError,
    RepeatLeadIn,
    RepeatLeadOut,
    RepeatTimeoutExpired
)

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
from .velleman import Velleman  # NOQA
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
from .config import Config

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
    Barco,
    Blaupunkt,
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
    F121,
    F120,
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
    Audiovox,
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
    Velleman,
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


from . import high_precision_timers


class IRDecoder(object):
    def __init__(self, config=None):
        if config is None:
            config = Config()

        config._parent = self

        self.__config = config
        self.__decoders = deque()
        self.__last_code = None
        self.__timer = high_precision_timers.TimerUS()
        self.__running = False

        for i, decoder in enumerate(_DECODERS):
            for decoder_xml in self.__config:
                if decoder.name == decoder_xml.name:
                    self.__decoders.append(protocol_base.IrProtocolBase(decoder_xml))
                    break
            else:
                decoder = decoder()
                self.__decoders.append(decoder)
                decoder_xml = decoder.xml
                self.__config.append(decoder_xml)

        self.__last_decoder = None

    @property
    def config(self):
        return self.__config

    def __iter__(self):
        for decoder in self.__decoders:
            yield decoder

    def get_code_name(self, code):
        if self.__config.database_url:
            import requests
            try:
                response = requests.get(self.__config.database_url)
                if response.status_code != 200:
                    raise requests.ConnectionError
            except requests.ConnectionError:
                pass
            else:
                token = response.content
                response = requests.get(
                    self.__config.database_url + '/' + token + '/get_name',
                    params=dict(id=code.hexdecimal)
                )

                if response.status_code == 200:
                    code.name = response.content

    @property
    def last_used_decoder(self):
        return self.__last_decoder

    def __reset_last_code(self, code):
        code.unbind_released_callback(self.__reset_last_code)
        if code.decoder == self.__last_decoder:
            self.__last_code = None

    def decode(self, data, frequency=0):
        if self.__running:
            raise RuntimeError('Create a new decoder instance for each thread.')

        self.__running = True
        self.__timer.reset()

        if isinstance(data, protocol_base.IRCode):
            self.__running = False
            raise DecodeError('Input to be decoded must be RLC')

        if isinstance(data, tuple):
            data = list(data)

        if not isinstance(data, list):
            data = [[int(ord(x)) for x in data]]
        elif not isinstance(data[0], list):
            data = [[int(x) for x in data]]
        #
        # for i, rlc in enumerate(data):
        #     if len(rlc) < 3:
        #         if i + 1 < len(data):
        #             data[i + 1] = rlc + data[i + 1]
        #             continue
        #         return

        if self.__last_code is not None:
            if self.__last_code.decoder.frequency_match(frequency):
                if len(data) == 1 and data[0] == self.__last_code:
                    self.__last_code.repeat_timer.start(self.__timer)
                    self.__running = False
                    return self.__last_code

                code = None
                for rlc in data:
                    try:
                        code = self.__last_code.decoder.decode(rlc, frequency)
                    except DecodeError:
                        break
                    except (RepeatLeadIn, RepeatLeadOut, RepeatTimeoutExpired):
                        if len(data) == 1:
                            self.__running = False
                            return None

                if code is not None:
                    code.repeat_timer.start(self.__timer)
                    self.__last_code = code
                    self.__running = False
                    return code

        code = None

        for i, decoder in enumerate(self.__decoders):
            if not decoder.enabled:
                continue

            if frequency != 0:
                if not decoder.frequency_match(frequency):
                    continue

            for c in decoder:
                if c == data:
                    if decoder._last_code is not None:
                        if decoder._last_code != c:
                            decoder._last_code.repeat_timer.stop()

                    decoder._last_code = c
                    c.repeat_timer.start(self.__timer)
                    self.__last_code = c
                    self.__running = False
                    return c

            for rlc in data:
                try:
                    code = decoder.decode(rlc, frequency)
                except DecodeError:
                    break
                except (RepeatLeadIn, RepeatLeadOut, RepeatTimeoutExpired):
                    if len(data) == 1:
                        self.__running = False
                        return None

                    continue
            else:
                self.__last_decoder = decoder
                break

        if code is None:
            rlc = []
            for r in data:
                if len(r) > len(rlc):
                    rlc = r[:]

            if len(rlc) < 6:
                self.__running = False
                return None

            decoder = self.Universal
            try:
                code = decoder.decode(rlc, frequency)
            except DecodeError:
                self.__running = False
                return None

        self.__last_decoder = code.decoder
        code.bind_released_callback(self.__reset_last_code)
        code.repeat_timer.start(self.__timer)
        self.__last_code = code
        self.__running = False

        return code

    @property
    def enabled_decoders(self):
        res = []

        for decoder in self:
            if decoder.enabled:
                res += [decoder.name]

        return res

    @property
    def disabled_decoders(self):
        res = []

        for decoder in self:
            if not decoder.enabled:
                res += [decoder.name]

        return res

    def __get_decoder(self, cls):
        for decoder in self:
            if decoder.name == cls.name:
                return decoder

    @property
    def Universal(self):
        return Universal

    @property
    def AdNotham(self):
        return self.__get_decoder(AdNotham)

    @property
    def Aiwa(self):
        return self.__get_decoder(Aiwa)

    @property
    def Akai(self):
        return self.__get_decoder(Akai)

    @property
    def Akord(self):
        return self.__get_decoder(Akord)

    @property
    def Amino(self):
        return self.__get_decoder(Amino)

    @property
    def Amino56(self):
        return self.__get_decoder(Amino56)

    @property
    def Anthem(self):
        return self.__get_decoder(Anthem)

    @property
    def Apple(self):
        return self.__get_decoder(Apple)

    @property
    def Archer(self):
        return self.__get_decoder(Archer)

    @property
    def Arctech(self):
        return self.__get_decoder(Arctech)

    @property
    def Arctech38(self):
        return self.__get_decoder(Arctech38)

    @property
    def Audiovox(self):
        return self.__get_decoder(Audiovox)

    @property
    def Barco(self):
        return self.__get_decoder(Barco)

    @property
    def Blaupunkt(self):
        return self.__get_decoder(Blaupunkt)

    @property
    def Bose(self):
        return self.__get_decoder(Bose)

    @property
    def Bryston(self):
        return self.__get_decoder(Bryston)

    @property
    def CanalSat(self):
        return self.__get_decoder(CanalSat)

    @property
    def CanalSatLD(self):
        return self.__get_decoder(CanalSatLD)

    @property
    def Denon(self):
        return self.__get_decoder(Denon)

    @property
    def DenonK(self):
        return self.__get_decoder(DenonK)

    @property
    def Dgtec(self):
        return self.__get_decoder(Dgtec)

    @property
    def Digivision(self):
        return self.__get_decoder(Digivision)

    @property
    def DirecTV(self):
        return self.__get_decoder(DirecTV)

    @property
    def DirecTV0(self):
        return self.__get_decoder(DirecTV0)

    @property
    def DirecTV1(self):
        return self.__get_decoder(DirecTV1)

    @property
    def DirecTV2(self):
        return self.__get_decoder(DirecTV2)

    @property
    def DirecTV3(self):
        return self.__get_decoder(DirecTV3)

    @property
    def DirecTV4(self):
        return self.__get_decoder(DirecTV4)

    @property
    def DirecTV5(self):
        return self.__get_decoder(DirecTV5)

    @property
    def DishNetwork(self):
        return self.__get_decoder(DishNetwork)

    @property
    def DishPlayer(self):
        return self.__get_decoder(DishPlayer)

    @property
    def Dyson(self):
        return self.__get_decoder(Dyson)

    @property
    def Dyson2(self):
        return self.__get_decoder(Dyson2)

    @property
    def Elan(self):
        return self.__get_decoder(Elan)

    @property
    def Elunevision(self):
        return self.__get_decoder(Elunevision)

    @property
    def Emerson(self):
        return self.__get_decoder(Emerson)

    @property
    def Entone(self):
        return self.__get_decoder(Entone)

    @property
    def F12(self):
        return self.__get_decoder(F12)

    @property
    def F120(self):
        return self.__get_decoder(F120)

    @property
    def F121(self):
        return self.__get_decoder(F121)

    @property
    def F32(self):
        return self.__get_decoder(F32)

    @property
    def Fujitsu(self):
        return self.__get_decoder(Fujitsu)

    @property
    def Fujitsu128(self):
        return self.__get_decoder(Fujitsu128)

    @property
    def Fujitsu56(self):
        return self.__get_decoder(Fujitsu56)

    @property
    def GI4DTV(self):
        return self.__get_decoder(GI4DTV)

    @property
    def GICable(self):
        return self.__get_decoder(GICable)

    @property
    def GIRG(self):
        return self.__get_decoder(GIRG)

    @property
    def Grundig16(self):
        return self.__get_decoder(Grundig16)

    @property
    def Grundig1630(self):
        return self.__get_decoder(Grundig1630)

    @property
    def GuangZhou(self):
        return self.__get_decoder(GuangZhou)

    @property
    def GwtS(self):
        return self.__get_decoder(GwtS)

    @property
    def GXB(self):
        return self.__get_decoder(GXB)

    @property
    def Humax4Phase(self):
        return self.__get_decoder(Humax4Phase)

    @property
    def InterVideoRC201(self):
        return self.__get_decoder(InterVideoRC201)

    @property
    def IODATAn(self):
        return self.__get_decoder(IODATAn)

    @property
    def Jerrold(self):
        return self.__get_decoder(Jerrold)

    @property
    def JVC(self):
        return self.__get_decoder(JVC)

    @property
    def JVC48(self):
        return self.__get_decoder(JVC48)

    @property
    def JVC56(self):
        return self.__get_decoder(JVC56)

    @property
    def Kaseikyo(self):
        return self.__get_decoder(Kaseikyo)

    @property
    def Kaseikyo56(self):
        return self.__get_decoder(Kaseikyo56)

    @property
    def Kathrein(self):
        return self.__get_decoder(Kathrein)

    @property
    def Konka(self):
        return self.__get_decoder(Konka)

    @property
    def Logitech(self):
        return self.__get_decoder(Logitech)

    @property
    def Lumagen(self):
        return self.__get_decoder(Lumagen)

    @property
    def Lutron(self):
        return self.__get_decoder(Lutron)

    @property
    def Matsui(self):
        return self.__get_decoder(Matsui)

    @property
    def MCE(self):
        return self.__get_decoder(MCE)

    @property
    def MCIR2kbd(self):
        return self.__get_decoder(MCIR2kbd)

    @property
    def MCIR2mouse(self):
        return self.__get_decoder(MCIR2mouse)

    @property
    def Metz19(self):
        return self.__get_decoder(Metz19)

    @property
    def Mitsubishi(self):
        return self.__get_decoder(Mitsubishi)

    @property
    def MitsubishiK(self):
        return self.__get_decoder(MitsubishiK)

    @property
    def Motorola(self):
        return self.__get_decoder(Motorola)

    @property
    def NEC(self):
        return self.__get_decoder(NEC)

    @property
    def NEC48(self):
        return self.__get_decoder(NEC48)

    @property
    def NECf16(self):
        return self.__get_decoder(NECf16)

    @property
    def NECrnc(self):
        return self.__get_decoder(NECrnc)

    @property
    def NECx(self):
        return self.__get_decoder(NECx)

    @property
    def NECxf16(self):
        return self.__get_decoder(NECxf16)

    @property
    def Nokia(self):
        return self.__get_decoder(Nokia)

    @property
    def Nokia12(self):
        return self.__get_decoder(Nokia12)

    @property
    def Nokia32(self):
        return self.__get_decoder(Nokia32)

    @property
    def NovaPace(self):
        return self.__get_decoder(NovaPace)

    @property
    def NRC16(self):
        return self.__get_decoder(NRC16)

    @property
    def NRC1632(self):
        return self.__get_decoder(NRC1632)

    @property
    def NRC17(self):
        return self.__get_decoder(NRC17)

    @property
    def Ortek(self):
        return self.__get_decoder(Ortek)

    @property
    def OrtekMCE(self):
        return self.__get_decoder(OrtekMCE)

    @property
    def PaceMSS(self):
        return self.__get_decoder(PaceMSS)

    @property
    def Panasonic(self):
        return self.__get_decoder(Panasonic)

    @property
    def Panasonic2(self):
        return self.__get_decoder(Panasonic2)

    @property
    def PanasonicOld(self):
        return self.__get_decoder(PanasonicOld)

    @property
    def PCTV(self):
        return self.__get_decoder(PCTV)

    @property
    def PID0001(self):
        return self.__get_decoder(PID0001)

    @property
    def PID0003(self):
        return self.__get_decoder(PID0003)

    @property
    def PID0004(self):
        return self.__get_decoder(PID0004)

    @property
    def PID0083(self):
        return self.__get_decoder(PID0083)

    @property
    def Pioneer(self):
        return self.__get_decoder(Pioneer)

    @property
    def Proton(self):
        return self.__get_decoder(Proton)

    @property
    def Proton40(self):
        return self.__get_decoder(Proton40)

    @property
    def RC5(self):
        return self.__get_decoder(RC5)

    @property
    def RC57F(self):
        return self.__get_decoder(RC57F)

    @property
    def RC57F57(self):
        return self.__get_decoder(RC57F57)

    @property
    def RC5x(self):
        return self.__get_decoder(RC5x)

    @property
    def RC6(self):
        return self.__get_decoder(RC6)

    @property
    def RC6620(self):
        return self.__get_decoder(RC6620)

    @property
    def RC6624(self):
        return self.__get_decoder(RC6624)

    @property
    def RC6632(self):
        return self.__get_decoder(RC6632)

    @property
    def RC6M16(self):
        return self.__get_decoder(RC6M16)

    @property
    def RC6M28(self):
        return self.__get_decoder(RC6M28)

    @property
    def RC6M32(self):
        return self.__get_decoder(RC6M32)

    @property
    def RC6M56(self):
        return self.__get_decoder(RC6M56)

    @property
    def RCA(self):
        return self.__get_decoder(RCA)

    @property
    def RCA38(self):
        return self.__get_decoder(RCA38)

    @property
    def RCA38Old(self):
        return self.__get_decoder(RCA38Old)

    @property
    def RCAOld(self):
        return self.__get_decoder(RCAOld)

    @property
    def RCMM(self):
        return self.__get_decoder(RCMM)

    @property
    def RECS800045(self):
        return self.__get_decoder(RECS800045)

    @property
    def RECS800068(self):
        return self.__get_decoder(RECS800068)

    @property
    def RECS800090(self):
        return self.__get_decoder(RECS800090)

    @property
    def Revox(self):
        return self.__get_decoder(Revox)

    @property
    def Roku(self):
        return self.__get_decoder(Roku)

    @property
    def Rs200(self):
        return self.__get_decoder(Rs200)

    @property
    def RTIRelay(self):
        return self.__get_decoder(RTIRelay)

    @property
    def Sampo(self):
        return self.__get_decoder(Sampo)

    @property
    def Samsung20(self):
        return self.__get_decoder(Samsung20)

    @property
    def Samsung36(self):
        return self.__get_decoder(Samsung36)

    @property
    def SamsungSMTG(self):
        return self.__get_decoder(SamsungSMTG)

    @property
    def ScAtl6(self):
        return self.__get_decoder(ScAtl6)

    @property
    def Sejin138(self):
        return self.__get_decoder(Sejin138)

    @property
    def Sejin156(self):
        return self.__get_decoder(Sejin156)

    @property
    def Sharp(self):
        return self.__get_decoder(Sharp)

    @property
    def Sharp1(self):
        return self.__get_decoder(Sharp1)

    @property
    def Sharp2(self):
        return self.__get_decoder(Sharp2)

    @property
    def SharpDVD(self):
        return self.__get_decoder(SharpDVD)

    @property
    def SIM2(self):
        return self.__get_decoder(SIM2)

    @property
    def Sky(self):
        return self.__get_decoder(Sky)

    @property
    def SkyHD(self):
        return self.__get_decoder(SkyHD)

    @property
    def SkyPlus(self):
        return self.__get_decoder(SkyPlus)

    @property
    def Somfy(self):
        return self.__get_decoder(Somfy)

    @property
    def Sony12(self):
        return self.__get_decoder(Sony12)

    @property
    def Sony15(self):
        return self.__get_decoder(Sony15)

    @property
    def Sony20(self):
        return self.__get_decoder(Sony20)

    @property
    def Sony8(self):
        return self.__get_decoder(Sony8)

    @property
    def StreamZap(self):
        return self.__get_decoder(StreamZap)

    @property
    def StreamZap57(self):
        return self.__get_decoder(StreamZap57)

    @property
    def Sunfire(self):
        return self.__get_decoder(Sunfire)

    @property
    def TDC38(self):
        return self.__get_decoder(TDC38)

    @property
    def TDC56(self):
        return self.__get_decoder(TDC56)

    @property
    def TeacK(self):
        return self.__get_decoder(TeacK)

    @property
    def Thomson(self):
        return self.__get_decoder(Thomson)

    @property
    def Thomson7(self):
        return self.__get_decoder(Thomson7)

    @property
    def Tivo(self):
        return self.__get_decoder(Tivo)

    @property
    def Velleman(self):
        return self.__get_decoder(Velleman)

    @property
    def Viewstar(self):
        return self.__get_decoder(Viewstar)

    @property
    def XBox360(self):
        return self.__get_decoder(XBox360)

    @property
    def XBoxOne(self):
        return self.__get_decoder(XBoxOne)
