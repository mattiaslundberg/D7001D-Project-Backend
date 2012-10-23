#!/usr/bin/python

import urllib2, time, sys
sys.path.append("..")
from awssqs import awssqs
from settings import * # Global variables

q = awssqs(FRONTEND_OUTGOING)

fout = open("outgoing_results.xml", "a+b")
while True:
	try:
		m = q.read()
		if m is not None:
			url = m.get_body()
			print "url %s" % url
			f = urllib2.urlopen(url)
			data = f.read()
			print "MSG: %s" % data
			fout.write(data)
			q.delete(m)
		else:
			print "empty"
			break

	except Exception,e:
		print e
		time.sleep(10)

fout.close()
