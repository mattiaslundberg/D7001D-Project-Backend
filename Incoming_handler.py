#!/usr/bin/python

from AWSSQS import AWSSQS
from calculated_db import db as _db
import os, time, socket
import urllib2
import boto.ec2


user = os.environ['LTU_USER']

FRONTEND_INCOMING = '12_LP1_SQS_D7001D_FRONTEND_INCOMING_%s' % user
FRONTEND_OUTGOING = '12_LP1_SQS_D7001D_FRONTEND_OUTGOING_%s' % user

logger = logging.getLogger('handleRequest')
handler = logging.FileHandler('/tmp/handleRequest.log')
logger.addHandler(handler) 
logger.setLevel(logging.INFO)

INTERVALL = 30
PRE_SLEEP_SHUTDOWN_TIME = 120

#http://docs.amazonwebservices.com/AWSEC2/latest/UserGuide/AESDG-chapter-instancedata.html
AMAZON_META_DATA_URL = "http://169.254.169.254/latest/meta-data/public-ipv4" # amazon public ip.
INSTANCE_ID_URL = "http://169.254.169.254/latest/meta-data/instance-id"

public_ip = ""
ip_checked = False
results = "/tmp/results/"
FRONTEND_ELB = 'FRONTENDelbgroup2'

''' using elb -- getdns() function
def public_ip():
	try:
		if public_ip:
			if ip_checked:
				return public_ip
			try:
		    	socket.inet_aton(public_ip)
		    	ip_checked = True
				# legal ipv4 address
				return public_ip
			except socket.error:
				# Not legal
				pass		

		f = urllib2.urlopen(AMAZON_META_DATA_URL)
		public_ip = f.read()
	except Exception, e:
		pass
	return public_ip
'''

def handleRequest(xmltext):
	print "TODO: Handle request", xmltext
	logger.info("TODO: Handle request")
	return (1, xmltext)

conn = None
dns = None

def getdns():
	try:			
		if conn is None:
			conn = boto.ec2.connect_to_region('eu-west-1')
		if dns is not None:
			return dns
		for e in conn.get_all_load_balancers(load_balancer_names=FRONTEND_ELB):
			dns = e.dns_name
			return dns
	except Exception, e:
		logger.error('Exception %s' % e)
		return "" # Should never happen...

try:
	db = _db()
except:
	pass

if not os.path.exists(results):
	os.makedirs(results)

try:
	qIncoming = AWSSQS(FRONTEND_INCOMING)
except:
	pass

try:
	qOutgoing = AWSSQS(FRONTEND_OUTGOING)
except:
	pass

while True:
	try:
		if not qIncoming:
			qIncoming = AWSSQS(FRONTEND_INCOMING)
		m = qIncoming.read()
		if m is None:
			# No job for me!
			time.sleep(INTERVALL)
			continue

		xmltext = m.get_body()
		if xmltext == "STOPINSTANCE": # Special case
			qIncoming.delete(m)
			#time.sleep(PRE_SLEEP_SHUTDOWN_TIME)
			
			f = urllib2.urlopen(INSTANCE_ID_URL)
			instance_id = f.read()

			conn = boto.ec2.connect_to_region('eu-west-1')

			# Stop this instance
			for r in conn.get_all_instances([instance_id]):
				for i in r.instances:
					i.add_tag('Name', 'delete-me_%s' % user)
					i.add_tag('action', 'delete')
					i.terminate()

			conn.close()
			time.sleep(600) # Just do nothing until system is shutdown


		logger.info("Got message %s" % xmltext)	
		requestID, result = handleRequest(xmltext)	

		if not db:
			db = _db()

		db.write(requestID, result)
		
		''' old style
		f = open(results+requestID+".xml","a+b")
		f.write(result)
		f.close()
		'''

		logger.info("Result written %s" % xmltext)

		if not qOutgoing:
			qOutgoing = AWSSQS(FRONTEND_INCOMING)

		qOutgoing.write("http://%s:8080/?requestid=%s" % (getdns(), requestID+".xml"))

		qIncoming.delete(m)
	except Exception, e:
		logger.error('Exception %s' % e)
		print e
		time.sleep(60)
