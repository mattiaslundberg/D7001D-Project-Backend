#!/usr/bin/python

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn
import logging
import threading
import commands
import urlparse
import os

logger = logging.getLogger('webserver')
handler = logging.FileHandler('/tmp/webserver.log')
logger.addHandler(handler) 
logger.setLevel(logging.INFO)

run_port = 8080

class Handler(BaseHTTPRequestHandler):
	""" Handle HTTP requests """
	
	def do_GET(self):
		""" Handle GET requests """
		# ONLY HEALTHCHECK
		self.send_response(200)
		self.send_header('Content-type','text/html')
		self.end_headers()

		qs = {}
		path = self.path
		if '?' in path:
			path, tmp = path.split('?', 1)
			qs = urlparse.parse_qs(tmp)
			if qs.has_key('requestid'):
				requestid = qs['requestid'][0]
				# TODO pick from database
				self.wfile.write(requestid)
				return

		self.wfile.write('You did not write GET /?requestid=123')
		
	def do_POST(self):
		""" Handle post requests """
		try:
			logger.info('POST Request') # For debug purposes
			# Get the parameters as a list
			param = urlparse.parse_qs(self.rfile.read(int(self.headers['Content-Length'])))
			logger.info('POST Parameters %s' % param)
		except Exception, e:
			# Always log exceptions
			logger.error('Exception %s' % e)

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	""" Add thread support for the http server 
	each request will be served in separate thread """

if __name__ == '__main__': # If running directly
	server = ThreadedHTTPServer(('', run_port), Handler)
	logger.info('Starting server on port %s' % run_port)
	print 'Listening on port %s' % run_port
	server.serve_forever()
