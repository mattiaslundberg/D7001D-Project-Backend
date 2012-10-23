#!/usr/bin/python
import commands
import socket
import time
import struct
import sys

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
		for ce in xrange(1,9):
			for si in xrange(0,1):
				for f in commands.getoutput("ls ../pkt").split('\n'):
					print max_tests
					s = socket.socket(
						socket.AF_INET, socket.SOCK_STREAM)
					s.connect(('wsn.d7001d.mlundberg.se', 12345))
					f_open = open('../pkt/%s' % f)
					data = f_open.read()
					f_open.close()
					tosend = struct.pack('!IIBQI',ce,2,si,time.time()*1000,len(data))
					s.send(tosend + data)
					s.close()
					if max_tests < 0:
						sys.exit()
					max_tests-=1
		sleep(1)
