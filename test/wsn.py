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
	for f in ['ID10_120915-102613-588', 'ID10_120915-102624-828', 'ID10_120915-102636-588', 'ID10_120915-102655-518', 'ID10_120915-102619-198',  'ID10_120915-102630-918', 'ID10_120915-102642-258', 'ID10_120915-102700-708']:
		print f
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect(('localhost', 12345))
		s.send('%32d' % 10)
		s.send('%32d' % 10)
		s.send('%8d' % 1)
		s.send('%64d' % int(time.time() * 1000))
		o = open('../test_in/' + f, 'r')
		data = o.read()
		s.send('%32d' % len(data))
		s.send(data)
		s.close()
		time.sleep(1)
