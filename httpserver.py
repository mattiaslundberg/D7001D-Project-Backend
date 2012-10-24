#!/usr/bin/python

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn
from calculated_db import db as _db
import logging
import threading
import commands
import urlparse
import os
import re

from settings import *

logger = logging.getLogger('webserver')
handler = logging.FileHandler('/tmp/webserver.log')
logger.addHandler(handler) 
logger.setLevel(logging.INFO)

class Handler(BaseHTTPRequestHandler):
	""" Handle HTTP requests """
	db = None
	
	def do_GET(self):
		""" Handle GET requests """
		self.send_response(200)
		self.send_header('Content-type','text/html')
		self.end_headers()

		number = []
		if len(self.path) > 1:
			number = re.findall("RequestID([0-9]+)\.xml",self.path[1:])

		if len(number):
			requestid = number[0]
			data = self._getdbdata(int(requestid))
			if data is None:
				self.wfile.write("That result do not exist in database")
			else:
				self.wfile.write(data)
			return

		self.wfile.write('You did not write GET /RequestID123.xml')

	def _getdbdata(self, requestid):
		if self.db is None:
			self.db = _db()
		return self.db.read(requestid)
		
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	""" Add thread support for the http server 
	each request will be served in separate thread """

if __name__ == '__main__': # If running directly
	server = ThreadedHTTPServer(('', HTTP_PORT), Handler)
	logger.info('Starting server on port %s' % HTTP_PORT)
	print 'Listening on port %s' % HTTP_PORT
	server.serve_forever()
