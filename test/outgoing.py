#!/usr/bin/python

import urllib2, time, sys
sys.path.append("..")
from awssqs import awssqs
from settings import * # Global variables

q = awssqs(FRONTEND_OUTGOING, create = False)

while True:
	try:
		m = q.read()
		if m is not None:
			f = urllib2.urlopen(m.get_body())
			data = f.read()
			print "MSG: "+data
		else:
			print "empty"
	except Exception,e:
		print e

	time.sleep(10)

