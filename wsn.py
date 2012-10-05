#!/usr/bin/python

import SocketServer
import commands
import socket
import threading
import logging
from SocketServer import ThreadingMixIn
from dynamo import db as _db

logger = logging.getLogger('wsn')
handler = logging.FileHandler('/tmp/wsn.log')
logger.addHandler(handler) 
logger.setLevel(logging.INFO)


class WSNTCPHandler(SocketServer.BaseRequestHandler):
	"""
	Handle incomming requests
	
	Packet:			Field size (bits) (ALL fields should be unsigned)
	Cell id			32
	Node id			32
	Side (flags)	8	zero equals right side and one equals left side
	Timestamp		64	UTC timestamp in ms
	Size			32	tells amount of bytes of rawdata
	Rawdata			xx
	"""
	
	db = _db()
	
	def handle(self):
		# self.request is the TCP socket connected to the client
		self.cell = self.request.recv(32, socket.MSG_WAITALL)
		self.node = self.request.recv(32, socket.MSG_WAITALL)
		self.side = self.request.recv(8, socket.MSG_WAITALL)
		self.timestamp = self.request.recv(64, socket.MSG_WAITALL)
		self.size = self.request.recv(32, socket.MSG_WAITALL)
		try:
			self.data = self.request.recv(int(self.size), socket.MSG_WAITALL)
		except:
			return # Test helth
		
		
		# DEBUG
		logger.info("recived data")
		logger.info("cell %d" % int(self.cell))
		logger.info("node %d" % int(self.node))
		logger.info("side %d" % int(self.side))
		logger.info("timestamp %d" % int(self.timestamp))
		logger.info("size %d" % int(self.size))
		
		
		file_name = '/tmp/read-file-%s' % threading.current_thread().ident
		f = open(file_name, 'w')
		f.write(self.data)
		f.close()
		
		self.cartype = commands.getoutput("/home/ubuntu/process -f type -n 1 %s" % file_name)
		#print "cartype: %s" % self.cartype
		
		try:
			self.db.save_packet(int(self.cell), int(self.node), int(self.side), int(self.timestamp), int(self.cartype), self.data)
			logger.info("saved")
		except ValueError, e:
			logger.info('ValueError %s' % e)
		except Exception, e:
			logger.info('Exception %s' % e)
 
class ThreadingServer(ThreadingMixIn, SocketServer.TCPServer):
	pass

if __name__ == "__main__":
	logger.info("started")
	server = ThreadingServer(("0.0.0.0", 12345), WSNTCPHandler)
	server.serve_forever()
