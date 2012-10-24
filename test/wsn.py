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
	max_tests = 1000
	while True:
		for f in commands.getoutput("ls ../pkt").split('\n'):
			for ce in xrange(1,10):
				for si in xrange(0,2):
					print 'test %d ce=%d si=%d' % (max_tests, ce, si)
					s = socket.socket(
					socket.AF_INET, socket.SOCK_STREAM)
					s.connect(('wsnelbgroup2-1188430327.eu-west-1.elb.amazonaws.com', 12345))
					f_open = open('../pkt/%s' % f)
					data = f_open.read()
					f_open.close()
					tosend = struct.pack('!IIBQI',ce,2,si,time.time()*1000,len(data))
					s.send(tosend + data)
					s.close()
					if max_tests < 0:
						sys.exit()
					max_tests-=1
		print 'SLEEP 10 sek'
		sleep(10)
