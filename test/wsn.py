#!/usr/bin/python
import commands
import socket
import time
import struct

"""
Send some random testdata.

Packet:			Field size (bits) (ALL fields should be unsigned)
Cell id			32
Node id			32
Side (flags)	8	zero equals right side and one equals left side
Timestamp		64	UTC timestamp in ms
Size			32	tells amount of bytes of rawdata
Rawdata			xx
"""

if __name__ == '__main__':
	max_tests = 10000
	while True:
		for f in commands.getoutput("ls ../pkt").split('\n'):
			s = socket.socket(
				socket.AF_INET, socket.SOCK_STREAM)
			s.connect(('wsn.d7001d.mlundberg.se', 12345))
			f_open = open('../pkt/%s' % f)
			data = f_open.read()
			f_open.close()
			tosend = struct.pack('!IIBQI',1,2,0,time.time()*1000,len(data))
			s.send(tosend + data)
			s.close()
			if max_tests < 0:
				break
			max_tests-=1
