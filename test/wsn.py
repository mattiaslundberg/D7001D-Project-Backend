#!/usr/bin/python
import commands
import socket
import time

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
	max_tests = 100
	for f in commands.getoutput("ls ../pkt").split('\n'):
		s = socket.socket(
			socket.AF_INET, socket.SOCK_STREAM)
		s.connect(('wsnelbgroup2-1091503389.eu-west-1.elb.amazonaws.com', 12345))
		s.send('%32d' % 2)
		s.send('%32d' % 2)
		s.send('%8d' % 1)
		s.send('%64d' % time.time())
		f_open = open('../pkt/%s' % f)
		data = str(f_open.read())
		f_open.close()
		s.send('%32d' % len(data))
		s.send(data)
		s.close()
		if max_tests < 0:
			break
		max_tests -= 1
		time.sleep(1)
