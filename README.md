# pyIRDecoder

Finally an IR encoder/decoder for Python!!!

Supports Python 2.7 and 3.5+

Supports encoding and decoding on the following protocols.

* AdNotham
* Aiwa
* Akai
* Akord
* Amino
* Amino56
* Anthem
* Apple
* Archer
* Audiovox
* Barco
* Blaupunkt
* Bose
* Bryston
* CanalSat
* CanalSatLD
* Denon2
* Denon
* Denon1
* DenonK
* Dgtec
* Digivision
* DirecTV
* DishNetwork
* DishPlayer
* Dyson
* Dyson2
* Elan
* Elunevision
* Emerson
* Entone
* F12
* F120
* F121
* F32
* Fujitsu
* Fujitsu128
* Fujitsu56
* GICable
* GIRG
* GuangZhou
* GwtS
* GXB
* Humax4Phase
* InterVideoRC201
* IODATAn
* Jerrold
* JVC
* JVC48
* JVC56
* Kaseikyo
* Kaseikyo56
* Kathrein
* Konka
* Logitech
* Lumagen
* Lutron
* Matsui
* MCE
* MCIR2kbd
* MCIR2mouse
* Metz19
* Mitsubishi
* MitsubishiK
* Motorola
* NEC
* NEC48
* NECf16
* NECrnc
* NECx
* NECxf16
* Nokia
* Nokia12
* Nokia32
* NovaPace
* NRC16
* NRC1632
* NRC17
* Ortek
* OrtekMCE
* PaceMSS
* Panasonic
* Panasonic2
* PanasonicOld
* PCTV
* PID0001
* PID0003
* PID0004
* PID0083
* Pioneer
* Proton
* Proton40
* RC5
* RC57F
* RC57F57
* RC5x
* RC6
* RC6620
* RC6624
* RC6632
* RC6M16
* RC6M28
* RC6M32
* RC6M56
* RCA
* RCA38
* RCA38Old
* RCAOld
* RECS800045
* RECS800068
* RECS800090
* Revox
* Roku
* RTIRelay
* Sampo
* Samsung20
* Samsung36
* SamsungSMTG
* ScAtl6
* Sharp
* Sharp1
* Sharp2
* SharpDVD
* SIM2
* Sky
* SkyHD
* SkyPlus
* Somfy
* Sony12
* Sony15
* Sony20
* Sony8
* StreamZap
* StreamZap57
* Sunfire
* TDC38
* TDC56
* TeacK
* Thomson
* Thomson7
* Tivo
* Viewstar
* XBox360
* XBoxOne


exceedingly easy to use.

    import pyIRDecoder
    
    ir_decoder = pyIRDecoder.IrDecoder()
    ir_encoder = pyIRDecoder.IrEncoder()
    
    # the RLC you want to have dcoded most IR receivers 
    # will also provide the modulation frequency
    rlc = []
    frequency = 0
    
    code = ir_decoder.decode(rlc, frequency)
    if code is not None:
        print(code)
        
This is the quick and dirty, it can get more complex and I am also working on a cached code system and also a server
based lookup to provide a user friendls name for the IR code.

The returned code from a decode is a pyIRDecoder.protocol_base.IRCode object. look at that object to see what is 
available. Some examples are converting the code to an int, getting the code as hex, original and normalized rlc, 
original and normalized pronto, original and normalized Media Center code (rounded to the nearest 50us) (pronto and rlc)
plus many more.

You can also set the frequency matching and also burst patching thresholds per protocol. and also enable and disable 
the use of a protocol in the decoder.

The average decode time with all protocols enabled is 2 milliseconds.

There are some protocols that will "bump heads" and you may have to disable a protocl that is doing this an example is 
Tivo and NEC.

 