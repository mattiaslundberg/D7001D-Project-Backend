#!/usr/bin/python

from awssqs import awssqs
from calculated_db import db as _db
import os, time, socket
import urllib2
import boto.ec2
from settings import * # Global variables
from myparser import *
import logging

logger = logging.getLogger('handleRequest')
handler = logging.FileHandler('/tmp/handleRequest.log')
logger.addHandler(handler) 
logger.setLevel(logging.INFO)

#http://docs.amazonwebservices.com/AWSEC2/latest/UserGuide/AESDG-chapter-instancedata.html
AMAZON_META_DATA_URL_INSTANCE_ID = "http://169.254.169.254/latest/meta-data/instance-id"

public_ip = ""
ip_checked = False
results = "/tmp/results/"

conn = None
dns = None

def handleRequest(xmltext):
	return parse(xmltext)

def getdns():
	try:
		if dns is not None:
			return dns
		if conn is None:
			conn = boto.ec2.connect_to_region('eu-west-1')
		for e in conn.get_all_load_balancers(load_balancer_names = FRONTEND_ELB):
			dns = e.dns_name
			return dns
	except Exception, e:
		logger.error('Exception %s' % e)
		return "localhost" # Should never happen...

if not os.path.exists(results):
	os.makedirs(results)

db = None
qIncoming = None
qOutgoing = None
c = 0

while True:
	try:
		if not qIncoming:
			qIncoming = awssqs(FRONTEND_INCOMING)
		if not qOutgoing:
			qOutgoing = awssqs(FRONTEND_OUTGOING)

		m = qIncoming.read()
		if m is None:
			# No job for me!
			print "no job"
			#time.sleep(INTERVALL)
			time.sleep(10)
			continue

		xmltext = m.get_body()
		if xmltext == "STOPINSTANCE": # Special case
			
			f = urllib2.urlopen(AMAZON_META_DATA_URL_INSTANCE_ID)
			instance_id = f.read()

			conn = boto.ec2.connect_to_region('eu-west-1')

			qIncoming.delete(m)

			# Stop this instance
			for r in conn.get_all_instances([instance_id]):
				for i in r.instances:
					i.add_tag('Name', 'delete-me_%s' % user)
					i.add_tag('action', 'delete')
					i.stop()

			conn.close()
			time.sleep(600) # Just do nothing until system shutdown
			continue


		logger.info("Got message %s" % xmltext)
		print "Got message %s" % xmltext
		result, requestID = handleRequest(xmltext)

		if not db:
			db = _db()

		print "Writing result %s" % result
		db.write(requestID, result)

		logger.info("Result written %s" % xmltext)

		if not qOutgoing:
			qOutgoing = awssqs(FRONTEND_INCOMING)

		qOutgoing.write("http://%s:%s/?requestid=%s" % (getdns(), HTTP_PORT, requestID))

		qIncoming.delete(m)
	except Exception, e:
		logger.error('Exception %s' % e)
		time.sleep(10)
		print e
		c +=1
		if c >= 10: # Reset
			db = None
			qIncoming = None
			qOutgoing = None
			c = 0

