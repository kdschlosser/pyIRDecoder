from .. import IRException  # NOQA
from .. import TooManyBitsError  # NOQA
from .. import NotEnoughBitsError  # NOQA
from .. import LeadInError  # NOQA
from .. import LeadOutError  # NOQA
from .. import EncodeError  # NOQA
from .. import DecodeError  # NOQA
from .. import IRStreamError  # NOQA
from .. import RepeatTimeoutExpired  # NOQA
from .. import RepeatLeadInError  # NOQA
from .. import RepeatLeadOutError  # NOQA
from .. import ExpectingMoreData  # NOQA

from .. import ir_code  # NOQA
from .. import code_wrapper  # NOQA
from .. import protocol_base  # NOQA

from .ad_notham import AdNotham as _AdNotham  # NOQA
from .aiwa import Aiwa as _Aiwa  # NOQA
from .akai import Akai as _Akai  # NOQA
from .akord import Akord as _Akord  # NOQA
from .amino import Amino as _Amino  # NOQA
from .amino56 import Amino56 as _Amino56  # NOQA
from .anthem import Anthem as _Anthem  # NOQA
from .apple import Apple as _Apple  # NOQA
from .archer import Archer as _Archer  # NOQA
from .arctech import Arctech as _Arctech  # NOQA
from .arctech38 import Arctech38 as _Arctech38  # NOQA
from .audiovox import Audiovox as _Audiovox  # NOQA
from .barco import Barco as _Barco  # NOQA
from .blaupunkt import Blaupunkt as _Blaupunkt  # NOQA
from .bose import Bose as _Bose  # NOQA
from .bryston import Bryston as _Bryston  # NOQA
from .canalsat import CanalSat as _CanalSat  # NOQA
from .canalsatld import CanalSatLD as _CanalSatLD  # NOQA
from .denon import Denon as _Denon  # NOQA
from .denon_k import DenonK as _DenonK  # NOQA
from .dgtec import Dgtec as _Dgtec  # NOQA
from .digivision import Digivision as _Digivision  # NOQA
from .directv import DirecTV as _DirecTV  # NOQA
from .directv0 import DirecTV0 as _DirecTV0  # NOQA
from .directv1 import DirecTV1 as _DirecTV1  # NOQA
from .directv2 import DirecTV2 as _DirecTV2  # NOQA
from .directv3 import DirecTV3 as _DirecTV3  # NOQA
from .directv4 import DirecTV4 as _DirecTV4  # NOQA
from .directv5 import DirecTV5 as _DirecTV5  # NOQA
from .dishnetwork import DishNetwork as _DishNetwork  # NOQA
from .dishplayer import DishPlayer as _DishPlayer  # NOQA
from .dyson import Dyson as _Dyson  # NOQA
from .dyson2 import Dyson2 as _Dyson2  # NOQA
from .elan import Elan as _Elan  # NOQA
from .elunevision import Elunevision as _Elunevision  # NOQA
from .emerson import Emerson as _Emerson  # NOQA
from .entone import Entone as _Entone  # NOQA
from .epson import Epson as _Epson  # NOQA
from .f12 import F12 as _F12  # NOQA
from .f32 import F32 as _F32  # NOQA
from .f120 import F120 as _F120  # NOQA
from .f121 import F121 as _F121  # NOQA
from .fujitsu import Fujitsu as _Fujitsu  # NOQA
from .fujitsu56 import Fujitsu56 as _Fujitsu56  # NOQA
from .fujitsu128 import Fujitsu128 as _Fujitsu128  # NOQA
from .gi4dtv import GI4DTV as _GI4DTV  # NOQA
from .gicable import GICable as _GICable  # NOQA
from .girg import GIRG as _GIRG  # NOQA
from .grundig16 import Grundig16 as _Grundig16  # NOQA
from .grundig1630 import Grundig1630 as _Grundig1630  # NOQA
from .guangzhou import GuangZhou as _GuangZhou  # NOQA
from .gwts import GwtS as _GwtS  # NOQA
from .gxb import GXB as _GXB  # NOQA
from .humax4phase import Humax4Phase as _Humax4Phase  # NOQA
from .intervideorc201 import InterVideoRC201 as _InterVideoRC201  # NOQA
from .iodatan import IODATAn as _IODATAn  # NOQA
from .jerrold import Jerrold as _Jerrold  # NOQA
from .jvc import JVC as _JVC  # NOQA
from .jvc48 import JVC48 as _JVC48  # NOQA
from .jvc56 import JVC56 as _JVC56  # NOQA
from .kaseikyo import Kaseikyo as _Kaseikyo  # NOQA
from .kaseikyo56 import Kaseikyo56 as _Kaseikyo56  # NOQA
from .kathrein import Kathrein as _Kathrein  # NOQA
from .konka import Konka as _Konka  # NOQA
from .logitech import Logitech as _Logitech  # NOQA
from .lumagen import Lumagen as _Lumagen  # NOQA
from .lutron import Lutron as _Lutron  # NOQA
from .matsui import Matsui as _Matsui  # NOQA
from .mce import MCE as _MCE  # NOQA
from .mcir2kbd import MCIR2kbd as _MCIR2kbd  # NOQA
from .mcir2mouse import MCIR2mouse as _MCIR2mouse  # NOQA
from .metz19 import Metz19 as _Metz19  # NOQA
from .mitsubishi import Mitsubishi as _Mitsubishi  # NOQA
from .mitsubishik import MitsubishiK as _MitsubishiK  # NOQA
from .motorola import Motorola as _Motorola  # NOQA
from .nec import NEC as _NEC  # NOQA
from .nec48 import NEC48 as _NEC48  # NOQA
from .necf16 import NECf16 as _NECf16  # NOQA
from .necrnc import NECrnc as _NECrnc  # NOQA
from .necx import NECx as _NECx  # NOQA
from .necxf16 import NECxf16 as _NECxf16  # NOQA
from .necyamaha import NECYamaha as _NECYamaha  # NOQA
from .nokia import Nokia as _Nokia  # NOQA
from .nokia12 import Nokia12 as _Nokia12  # NOQA
from .nokia32 import Nokia32 as _Nokia32  # NOQA
from .novapace import NovaPace as _NovaPace  # NOQA
from .nrc16 import NRC16 as _NRC16  # NOQA
from .nrc17 import NRC17 as _NRC17  # NOQA
from .nrc1632 import NRC1632 as _NRC1632  # NOQA
from .ortek import Ortek as _Ortek  # NOQA
from .ortekmce import OrtekMCE as _OrtekMCE  # NOQA
from .pacemss import PaceMSS as _PaceMSS  # NOQA
from .panasonic import Panasonic as _Panasonic  # NOQA
from .panasonic2 import Panasonic2 as _Panasonic2  # NOQA
from .panasonicold import PanasonicOld as _PanasonicOld  # NOQA
from .pctv import PCTV as _PCTV  # NOQA
from .pid0001 import PID0001 as _PID0001  # NOQA
from .pid0003 import PID0003 as _PID0003  # NOQA
from .pid0004 import PID0004 as _PID0004  # NOQA
from .pid0083 import PID0083 as _PID0083  # NOQA
from .pioneer import Pioneer as _Pioneer  # NOQA
from .pioneermix import PioneerMix as _PioneerMix  # NOQA
from .proton import Proton as _Proton  # NOQA
from .proton40 import Proton40 as _Proton40  # NOQA
from .rc5 import RC5 as _RC5  # NOQA
from .rc5x import RC5x as _RC5x  # NOQA
from .rc6 import RC6 as _RC6  # NOQA
from .rc6m16 import RC6M16 as _RC6M16  # NOQA
from .rc6m28 import RC6M28 as _RC6M28  # NOQA
from .rc6m32 import RC6M32 as _RC6M32  # NOQA
from .rc6m56 import RC6M56 as _RC6M56  # NOQA
from .rc6mbit import RC6MBIT as _RC6MBIT  # NOQA
from .rc57f import RC57F as _RC57F  # NOQA
from .rc57f57 import RC57F57 as _RC57F57  # NOQA
from .rc6620 import RC6620 as _RC6620  # NOQA
from .rc6624 import RC6624 as _RC6624  # NOQA
from .rc6632 import RC6632 as _RC6632  # NOQA
from .rca import RCA as _RCA  # NOQA
from .rca38 import RCA38 as _RCA38  # NOQA
from .rca38old import RCA38Old as _RCA38Old  # NOQA
from .rcaold import RCAOld as _RCAOld  # NOQA
from .rcmm12 import RCMM12 as _RCMM12  # NOQA
from .rcmm24 import RCMM24 as _RCMM24  # NOQA
from .rcmmoem import RCMMOEM as _RCMMOEM  # NOQA
from .recs800045 import RECS800045 as _RECS800045  # NOQA
from .recs800068 import RECS800068 as _RECS800068  # NOQA
from .recs800090 import RECS800090 as _RECS800090  # NOQA
from .revox import Revox as _Revox  # NOQA
from .roku import Roku as _Roku  # NOQA
from .rs200 import Rs200 as _Rs200  # NOQA
from .rti_relay import RTIRelay as _RTIRelay  # NOQA
from .sampo import Sampo as _Sampo  # NOQA
from .samsung20 import Samsung20 as _Samsung20  # NOQA
from .samsung36 import Samsung36 as _Samsung36  # NOQA
from .samsungsmtg import SamsungSMTG as _SamsungSMTG  # NOQA
from .scatl6 import ScAtl6 as _ScAtl6  # NOQA
from .sharp import Sharp as _Sharp  # NOQA
from .sharp1 import Sharp1 as _Sharp1  # NOQA
from .sharp2 import Sharp2 as _Sharp2  # NOQA
from .sharpdvd import SharpDVD as _SharpDVD  # NOQA
from .sim2 import SIM2 as _SIM2  # NOQA
from .sky import Sky as _Sky  # NOQA
from .sky_hd import SkyHD as _SkyHD  # NOQA
from .sky_plus import SkyPlus as _SkyPlus  # NOQA
from .solidtek16 import SolidTek16 as _SolidTek16  # NOQA
from .somfy import Somfy as _Somfy  # NOQA
from .sony8 import Sony8 as _Sony8  # NOQA
from .sony12 import Sony12 as _Sony12  # NOQA
from .sony15 import Sony15 as _Sony15  # NOQA
from .sony20 import Sony20 as _Sony20  # NOQA
from .sonydsp import SonyDSP as _SonyDSP  # NOQA
from .streamzap import StreamZap as _StreamZap  # NOQA
from .streamzap57 import StreamZap57 as _StreamZap57  # NOQA
from .sunfire import Sunfire as _Sunfire  # NOQA
from .tdc38 import TDC38 as _TDC38  # NOQA
from .tdc56 import TDC56 as _TDC56  # NOQA
from .teack import TeacK as _TeacK  # NOQA
from .thomson import Thomson as _Thomson  # NOQA
from .thomson7 import Thomson7 as _Thomson7  # NOQA
from .tivo import Tivo as _Tivo  # NOQA
from .universal import Universal as _Universal  # NOQA
from .velleman import Velleman as _Velleman  # NOQA
from .viewstar import Viewstar as _Viewstar  # NOQA
from .whynter import Whynter as _Whynter  # NOQA
from .x10 import X10 as _X10  # NOQA
from .x10n import X10n as _X10n  # NOQA
from .x10_18 import X10_18 as _X10_18  # NOQA
from .x10_8 import X10_8 as _X10_8  # NOQA
from .xbox_360 import XBox360 as _XBox360  # NOQA
from .xbox_one import XBoxOne as _XBoxOne  # NOQA
from .xiaomi import Xiaomi as _Xiaomi  # NOQA
from .xmp import XMP as _XMP  # NOQA
from .zaptor36 import Zaptor36 as _Zaptor36  # NOQA
from .zaptor56 import Zaptor56 as _Zaptor56  # NOQA

from .. import high_precision_timers
from .. import thread_worker
from ..config import Config

import threading
from collections import deque
from typing import Optional

AdNotham: protocol_base.IrProtocolBase
Aiwa: protocol_base.IrProtocolBase
Akai: protocol_base.IrProtocolBase
Akord: protocol_base.IrProtocolBase
Amino: protocol_base.IrProtocolBase
Amino56: protocol_base.IrProtocolBase
Anthem: protocol_base.IrProtocolBase
Apple: protocol_base.IrProtocolBase
Archer: protocol_base.IrProtocolBase
Arctech: protocol_base.IrProtocolBase
Arctech38: protocol_base.IrProtocolBase
Audiovox: protocol_base.IrProtocolBase
Barco: protocol_base.IrProtocolBase
Blaupunkt: protocol_base.IrProtocolBase
Bose: protocol_base.IrProtocolBase
Bryston: protocol_base.IrProtocolBase
CanalSat: protocol_base.IrProtocolBase
CanalSatLD: protocol_base.IrProtocolBase
Denon: protocol_base.IrProtocolBase
DenonK: protocol_base.IrProtocolBase
Dgtec: protocol_base.IrProtocolBase
Digivision: protocol_base.IrProtocolBase
DirecTV: protocol_base.IrProtocolBase
DirecTV0: protocol_base.IrProtocolBase
DirecTV1: protocol_base.IrProtocolBase
DirecTV2: protocol_base.IrProtocolBase
DirecTV3: protocol_base.IrProtocolBase
DirecTV4: protocol_base.IrProtocolBase
DirecTV5: protocol_base.IrProtocolBase
DishNetwork: protocol_base.IrProtocolBase
DishPlayer: protocol_base.IrProtocolBase
Dyson: protocol_base.IrProtocolBase
Dyson2: protocol_base.IrProtocolBase
Elan: protocol_base.IrProtocolBase
Elunevision: protocol_base.IrProtocolBase
Emerson: protocol_base.IrProtocolBase
Entone: protocol_base.IrProtocolBase
Epson: protocol_base.IrProtocolBase
F12: protocol_base.IrProtocolBase
F32: protocol_base.IrProtocolBase
F120: protocol_base.IrProtocolBase
F121: protocol_base.IrProtocolBase
Fujitsu: protocol_base.IrProtocolBase
Fujitsu56: protocol_base.IrProtocolBase
Fujitsu128: protocol_base.IrProtocolBase
GI4DTV: protocol_base.IrProtocolBase
GICable: protocol_base.IrProtocolBase
GIRG: protocol_base.IrProtocolBase
Grundig16: protocol_base.IrProtocolBase
Grundig1630: protocol_base.IrProtocolBase
GuangZhou: protocol_base.IrProtocolBase
GwtS: protocol_base.IrProtocolBase
GXB: protocol_base.IrProtocolBase
Humax4Phase: protocol_base.IrProtocolBase
InterVideoRC201: protocol_base.IrProtocolBase
IODATAn: protocol_base.IrProtocolBase
Jerrold: protocol_base.IrProtocolBase
JVC: protocol_base.IrProtocolBase
JVC48: protocol_base.IrProtocolBase
JVC56: protocol_base.IrProtocolBase
Kaseikyo: protocol_base.IrProtocolBase
Kaseikyo56: protocol_base.IrProtocolBase
Kathrein: protocol_base.IrProtocolBase
Konka: protocol_base.IrProtocolBase
Logitech: protocol_base.IrProtocolBase
Lumagen: protocol_base.IrProtocolBase
Lutron: protocol_base.IrProtocolBase
Matsui: protocol_base.IrProtocolBase
MCE: protocol_base.IrProtocolBase
MCIR2kbd: protocol_base.IrProtocolBase
MCIR2mouse: protocol_base.IrProtocolBase
Metz19: protocol_base.IrProtocolBase
Mitsubishi: protocol_base.IrProtocolBase
MitsubishiK: protocol_base.IrProtocolBase
Motorola: protocol_base.IrProtocolBase
NEC: protocol_base.IrProtocolBase
NEC48: protocol_base.IrProtocolBase
NECf16: protocol_base.IrProtocolBase
NECrnc: protocol_base.IrProtocolBase
NECx: protocol_base.IrProtocolBase
NECxf16: protocol_base.IrProtocolBase
NECYamaha: protocol_base.IrProtocolBase
Nokia: protocol_base.IrProtocolBase
Nokia12: protocol_base.IrProtocolBase
Nokia32: protocol_base.IrProtocolBase
NovaPace: protocol_base.IrProtocolBase
NRC16: protocol_base.IrProtocolBase
NRC17: protocol_base.IrProtocolBase
NRC1632: protocol_base.IrProtocolBase
Ortek: protocol_base.IrProtocolBase
OrtekMCE: protocol_base.IrProtocolBase
PaceMSS: protocol_base.IrProtocolBase
Panasonic: protocol_base.IrProtocolBase
Panasonic2: protocol_base.IrProtocolBase
PanasonicOld: protocol_base.IrProtocolBase
PCTV: protocol_base.IrProtocolBase
PID0001: protocol_base.IrProtocolBase
PID0003: protocol_base.IrProtocolBase
PID0004: protocol_base.IrProtocolBase
PID0083: protocol_base.IrProtocolBase
Pioneer: protocol_base.IrProtocolBase
PioneerMix: protocol_base.IrProtocolBase
Proton: protocol_base.IrProtocolBase
Proton40: protocol_base.IrProtocolBase
RC5: protocol_base.IrProtocolBase
RC5x: protocol_base.IrProtocolBase
RC6: protocol_base.IrProtocolBase
RC6M16: protocol_base.IrProtocolBase
RC6M28: protocol_base.IrProtocolBase
RC6M32: protocol_base.IrProtocolBase
RC6M56: protocol_base.IrProtocolBase
RC6MBIT: protocol_base.IrProtocolBase
RC57F: protocol_base.IrProtocolBase
RC57F57: protocol_base.IrProtocolBase
RC6620: protocol_base.IrProtocolBase
RC6624: protocol_base.IrProtocolBase
RC6632: protocol_base.IrProtocolBase
RCA: protocol_base.IrProtocolBase
RCA38: protocol_base.IrProtocolBase
RCA38Old: protocol_base.IrProtocolBase
RCAOld: protocol_base.IrProtocolBase
RCMM12: protocol_base.IrProtocolBase
RCMM24: protocol_base.IrProtocolBase
RCMMOEM: protocol_base.IrProtocolBase
RECS800045: protocol_base.IrProtocolBase
RECS800068: protocol_base.IrProtocolBase
RECS800090: protocol_base.IrProtocolBase
Revox: protocol_base.IrProtocolBase
Roku: protocol_base.IrProtocolBase
Rs200: protocol_base.IrProtocolBase
RTIRelay: protocol_base.IrProtocolBase
Sampo: protocol_base.IrProtocolBase
Samsung20: protocol_base.IrProtocolBase
Samsung36: protocol_base.IrProtocolBase
SamsungSMTG: protocol_base.IrProtocolBase
ScAtl6: protocol_base.IrProtocolBase
Sharp: protocol_base.IrProtocolBase
Sharp1: protocol_base.IrProtocolBase
Sharp2: protocol_base.IrProtocolBase
SharpDVD: protocol_base.IrProtocolBase
SIM2: protocol_base.IrProtocolBase
Sky: protocol_base.IrProtocolBase
SkyHD: protocol_base.IrProtocolBase
SkyPlus: protocol_base.IrProtocolBase
SolidTek16: protocol_base.IrProtocolBase
Somfy: protocol_base.IrProtocolBase
Sony8: protocol_base.IrProtocolBase
Sony12: protocol_base.IrProtocolBase
Sony15: protocol_base.IrProtocolBase
Sony20: protocol_base.IrProtocolBase
SonyDSP: protocol_base.IrProtocolBase
StreamZap: protocol_base.IrProtocolBase
StreamZap57: protocol_base.IrProtocolBase
Sunfire: protocol_base.IrProtocolBase
TDC38: protocol_base.IrProtocolBase
TDC56: protocol_base.IrProtocolBase
TeacK: protocol_base.IrProtocolBase
Thomson: protocol_base.IrProtocolBase
Thomson7: protocol_base.IrProtocolBase
Tivo: protocol_base.IrProtocolBase
Universal: protocol_base.IrProtocolBase
Velleman: protocol_base.IrProtocolBase
Viewstar: protocol_base.IrProtocolBase
Whynter: protocol_base.IrProtocolBase
X10: protocol_base.IrProtocolBase
X10n: protocol_base.IrProtocolBase
X10_18: protocol_base.IrProtocolBase
X10_8: protocol_base.IrProtocolBase
XBox360: protocol_base.IrProtocolBase
XBoxOne: protocol_base.IrProtocolBase
Xiaomi: protocol_base.IrProtocolBase
XMP: protocol_base.IrProtocolBase
Zaptor36: protocol_base.IrProtocolBase
Zaptor56: protocol_base.IrProtocolBase

config: Config

enabled_decoders: list
disabled_decoders: list
last_used_decoder: protocol_base.IrProtocolBase


# noinspection PyUnusedLocal
def bind_callback(callback: callable):
    pass


def unbind_callback():
    pass


def close():
    pass


# noinspection PyUnusedLocal
def stream_decode(data: list, frequency: int = 0):
    pass


# noinspection PyUnusedLocal
def decode(data: list, frequency: int = 0) -> Optional[protocol_base.IRCode]:
    pass


def __iter__():
    pass


# noinspection PyUnusedLocal
def append(data: list, frequency: int):
    pass


def run():
    pass


# noinspection PyUnusedLocal
def load_config(config_data):
    pass


class DecodeThread(threading.Thread):

    def __init__(self, decoder):
        self.decoder = decoder
        self.stop_event = threading.Event()
        self.buffer_event = threading.Event()
        self.buffer_lock = threading.Lock()
        self.decode_universal = False
        self.buffer = deque()
        self.my_timer = high_precision_timers.TimerUS()

        threading.Thread.__init__(self)

    def append(self, data, frequency):
        self.my_timer.reset()

        with self.buffer_lock:
            self.buffer.append((data, frequency))

        self.buffer_event.set()

    def run(self):
        while not self.stop_event.is_set():
            if self.decode_universal:
                self.buffer_event.wait(0.1)
                if not self.buffer_event.is_set():
                    with self.buffer_lock:
                        buf = []
                        frequency = 0
                        while self.buffer:
                            b, f = self.buffer.popleft()
                            if frequency != 0:
                                if f != frequency:
                                    self.buffer.appendleft((b, f))
                                    break

                            frequency = f
                            buf += b

                    if len(buf) > 6:
                        # noinspection PyProtectedMember
                        self.decoder._decode_universal(buf, frequency)
                    self.decode_universal = False
                    continue
            else:
                self.buffer_event.wait()

            self.buffer_event.clear()
            buf = []
            frequency = 0

            while self.buffer:
                b, f = self.buffer.popleft()
                if frequency != 0:
                    if f != frequency:
                        self.buffer.appendleft((b, f))
                        break

                frequency = f
                buf += b

            tmp_buf = []
            while buf:
                tmp_buf += [buf.pop(0)]

                if len(tmp_buf) > 3 and tmp_buf[-1] < -2000:
                    # noinspection PyProtectedMember
                    if self.decoder._decode(tmp_buf[:], frequency):
                        del tmp_buf[:]

            if tmp_buf:
                self.buffer.appendleft((tmp_buf, frequency))
                self.decode_universal = True
            else:
                self.decode_universal = False

    def stop(self):
        if self.is_alive():
            self.stop_event.set()
            self.buffer_event.set()
            self.join()
            

_process_threadworker = thread_worker.ProcessThreadWorker()
_timer_threadworker = thread_worker.TimerThreadWorker()


class FakeModule(object):
    _instance = None

    def __init__(self, config_data=None):
        import sys

        if FakeModule._instance is None:
            mod = sys.modules[__name__]
            # noinspection PyTypeChecker
            sys.modules[__name__] = self

        else:
            # noinspection PyProtectedMember
            mod = FakeModule._instance._original_module

        self.__doc__ = mod.__doc__
        self.__file__ = mod.__file__
        self.__loader__ = mod.__loader__
        self.__name__ = mod.__name__
        self.__package__ = mod.__package__
        self.__path__ = mod.__path__
        self.__spec__ = mod.__spec__
        self._original_module = mod
        
        if config_data is None:
            config_data = Config()

        config_data._parent = self

        self._config = config_data
        self._decoders = deque()
        self._last_code = None
        self._last_decoder = None
        self._timer = high_precision_timers.TimerUS()
        self._running = False
        self._repeat_code_lock = threading.Lock()
        self._decode_thread = None
        self._decode_callback = None

        import inspect

        decoders = [
            globals()[key] for key in sorted(list(globals().keys()))
            if inspect.isclass(globals()[key]) and
            issubclass(globals()[key], protocol_base.IrProtocolBase)
        ]

        for decoder in decoders:
            for decoder_xml in self._config:
                if decoder.__name__ == decoder_xml.name:
                    self._decoders.append(
                        decoder(self, decoder_xml)
                    )
                    break
            else:
                decoder = decoder(self)
                self._decoders.append(decoder)
                decoder_xml = decoder.xml
                self._config.append(decoder_xml)

        if FakeModule._instance is None:
            FakeModule._instance = self
        else:
            FakeModule._instance.__dict__.update(self.__dict__)

        _timer_threadworker.start()
        _process_threadworker.start()
                
    def __getattr__(self, item):
        if item in self.__dict__:
            return self.__dict__[item]
        
        for decoder in self._decoders:
            if decoder.__class__.__name__ == item:
                return decoder
            
        raise AttributeError(item)
    
    def bind_callback(self, callback):
        self._decode_callback = callback

    def unbind_callback(self):
        self._decode_callback = None

    def _decode_universal(self, rlc, frequency):
        if len(rlc) < 6:
            return False

        self._timer.reset()
        with self._repeat_code_lock:
            code = Universal.decode(rlc, frequency)
            if self._last_code is not None:
                if self._last_code == code:
                    self._last_code.repeat_timer.start(self._timer)
                    if self._decode_callback is not None:
                        _process_threadworker.add(
                            self._decode_callback,
                            self._last_code
                        )

                self._last_code.repeat_timer.stop()

            code.bind_released_callback(self.__reset_last_code)
            self._last_code = code
            self._last_code.repeat_timer.start(self._timer)
            if self._decode_callback is not None:
                _process_threadworker.add(
                    self._decode_callback,
                    self._last_code
                )

            return True

    def close(self):
        if self._decode_thread is not None:
            self._decode_thread.stop()
            self._decode_thread = None
        try:
            self.config.save()
        except:  # NOQA
            pass

        _timer_threadworker.stop()
        _process_threadworker.stop()

    @property
    def config(self):
        return self._config

    def __iter__(self):
        for decoder in self._decoders:
            yield decoder

    def get_code_name(self, code: protocol_base.IRCode):
        if self._config.database_url:
            import requests
            try:
                response = requests.get(self._config.database_url)
                if response.status_code != 200:
                    raise requests.ConnectionError
            except requests.ConnectionError:
                pass
            else:
                token = response.content
                response = requests.get(
                    self._config.database_url + '/' + token + '/get_name',
                    params=dict(id=code.hexdaecimal)
                )

                if response.status_code == 200:
                    code.name = response.content

    @property
    def last_used_decoder(self):
        return self._last_decoder

    def __reset_last_code(self, code):
        with self._repeat_code_lock:
            if code == self._last_code:
                if code.repeat_timer.is_running:
                    return

                self._last_code = None

            code.unbind_released_callback(self.__reset_last_code)

    def _decode(self, data, frequency):
        self._timer.reset()

        if frequency == 0:
            possible_decoders = list(
                decoder for decoder in self._decoders if decoder.enabled
            )
        else:
            possible_decoders = list(
                decoder for decoder in self._decoders
                if decoder.enabled and decoder.frequency_match(frequency)
            )

        with self._repeat_code_lock:
            if (
                self._last_code is not None and
                self._last_code.decoder in possible_decoders
            ):
                if data == self._last_code:
                    self._last_code.repeat_timer.start(self._timer)
                    if self._decode_callback is not None:
                        _process_threadworker.add(
                            self._decode_callback,
                            self._last_code
                        )

                    return True

                try:
                    code = self._last_code.decoder.decode(data, frequency)
                    if code != self._last_code:
                        self._last_code = code

                    self._last_code.repeat_timer.start(self._timer)

                    if self._decode_callback is not None:
                        _process_threadworker.add(
                            self._decode_callback,
                            self._last_code
                        )

                    return code

                except DecodeError:
                    pass
                except RepeatLeadInError:
                    self._last_decoder = self._last_code.decoder
                    return True

                except (RepeatLeadOutError, RepeatTimeoutExpired):
                    return True

            elif (
                self._last_decoder is not None and
                self._last_decoder in possible_decoders
            ):
                try:
                    code = self._last_decoder.decode(data, frequency)
                    if code != self._last_code:
                        self._last_code = code

                    self._last_code.repeat_timer.start(self._timer)

                    if self._decode_callback is not None:
                        _process_threadworker.add(
                            self._decode_callback,
                            self._last_code
                        )

                    return True

                except DecodeError:
                    pass
                except RepeatLeadInError:
                    if self._last_code is not None:
                        self._last_decoder = self._last_code.decoder
                        return True

                except (RepeatLeadOutError, RepeatTimeoutExpired):
                    return True

            for decoder in possible_decoders:
                for code in decoder:
                    if code == data:
                        # noinspection PyProtectedMember
                        if decoder._last_code is not None:
                            # noinspection PyProtectedMember
                            decoder._last_code.repeat_timer.stop()
                        break

                else:
                    try:
                        code = decoder.decode(data, frequency)
                    except DecodeError:
                        continue

                    except RepeatLeadInError:
                        self._last_decoder = decoder
                        return True

                    except (RepeatLeadOutError, RepeatTimeoutExpired):
                        return True

                code.bind_released_callback(self.__reset_last_code)
                self._last_decoder = decoder
                self._last_code = code
                code.repeat_timer.start(self._timer)

                if self._decode_callback is not None:
                    _process_threadworker.add(
                        self._decode_callback,
                        self._last_code
                    )

                return code

    def decode(
        self,
        data: list,
        frequency: int = 0
    ) -> Optional[protocol_base.IRCode]:
        if not data:
            return

        if isinstance(data, protocol_base.IRCode):
            frequency = data.frequency
            data = data.normalized_rlc

        elif isinstance(data, tuple):
            data = list(data)

        elif not isinstance(data, list):
            try:
                from .. import pronto
                frequency, data = pronto.pronto_to_rlc(data)
                data = [item for sublist in data for item in sublist]
            except:  # NOQA
                try:
                    data = [int(ord(x)) for x in data]
                except:  # NOQA
                    data = [int(x) for x in data]

        code = self._decode(data, frequency)
        if code is True:
            return None

        return code

    def stream_decode(self, data: list, frequency: int = 0):
        if not data:
            return

        if self._decode_thread is None:
            self._decode_thread = DecodeThread(self)
            self._decode_thread.start()

        if isinstance(data, protocol_base.IRCode):
            frequency = data.frequency
            data = [item for sublist in data for item in sublist]

        elif isinstance(data, tuple):
            data = list(data)

        elif not isinstance(data, list):
            try:
                from .. import pronto
                frequency, data = pronto.pronto_to_rlc(data)
                data = [item for sublist in data for item in sublist]
            except:  # NOQA
                try:
                    data = [int(ord(x)) for x in data]
                except:  # NOQA
                    data = [int(x) for x in data]

        self._decode_thread.append(data, frequency)

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

    def load_config(self, config_data):
        self.close()
        FakeModule(config_data)


__fake_module = FakeModule()
