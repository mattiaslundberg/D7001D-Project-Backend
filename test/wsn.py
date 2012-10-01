#!/usr/bin/python
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
	s = socket.socket(
		socket.AF_INET, socket.SOCK_STREAM)
	s.connect(('localhost', 12345))
	s.send('%32d' % 1)
	s.send('%32d' % 2)
	s.send('%8d' % 1)
	s.send('%64d' % time.time())
	data = "HELLO WORLD"
	s.send('%32d' % len(data))
	s.send(data)
	s.close()
