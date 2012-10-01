import SocketServer
import socket
from SocketServer import ThreadingMixIn
from dynamo import db as _db


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
	
	def __init__(self):
		self.db = _db()
	
	def handle(self):
		# self.request is the TCP socket connected to the client
		self.cell = self.request.recv(32, socket.MSG_WAITALL)
		self.node = self.request.recv(32, socket.MSG_WAITALL)
		self.side = self.request.recv(8, socket.MSG_WAITALL)
		self.timestamp = self.request.recv(64, socket.MSG_WAITALL)
		self.size = self.request.recv(32, socket.MSG_WAITALL)
		self.data = self.request.recv(int(self.size), socket.MSG_WAITALL)
		print "recived data"
		print "cell %d" % int(self.cell)
		print "node %d" % int(self.node)
		print "side %d" % int(self.side)
		print "timestamp %d" % int(self.timestamp)
		print "size %d" % int(self.size)
		print "data %s" % self.data
		
		self.cartype = commands.getoutput("echo 1")
		self.db.save_packet(int(self.cell), int(self.node), int(self.side), int(self.timestamp), self.cartype)
 
class ThreadingServer(ThreadingMixIn, SocketServer.TCPServer):
	pass

if __name__ == "__main__":
	server = ThreadingServer(("localhost", 12345), WSNTCPHandler)
	server.serve_forever()
