#!/usr/bin/python

from BaseHTTPServer import BaseHTTPSRequestHandler, HTTPSServer
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

def healthy(): # Can be used to check if localhost is 'healthy'
	return float(commands.getoutput("uptime | awk {'print $(NF-2)'} | awk -F ',' '{print $1}'")) < 1.2

class Handler(BaseHTTPSRequestHandler):
	""" Handle HTTP requests """
	
	def do_GET(self):
		""" Handle GET requests """
		# ONLY HEALTHCHECK
		self.send_response(200)
		self.send_header('Content-type','text/html')
		self.end_headers()
		self.wfile.write('OK')
		
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

class ThreadedHTTPServer(ThreadingMixIn, HTTPSServer):
	""" Add thread support for the http server 
	each request will be served in separate thread """

if __name__ == '__main__': # If running directly
	server = ThreadedHTTPServer(('', run_port), Handler)
	logger.info('Starting server on port %s' % run_port)
	print 'Listening on port %s' % run_port
	server.serve_forever()
