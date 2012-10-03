#!/usr/bin/python

from AWSSQS import AWSSQS
import os, time, socket
import urllib2

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

def handleRequest(xmltext):
	print "TODO: Handle request", xmltext
	logger.info("TODO: Handle request")
	return (1, xmltext)

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
			time.sleep(PRE_SLEEP_SHUTDOWN_TIME)
			
			f = urllib2.urlopen(INSTANCE_ID_URL)
			instance_id = f.read()

			import boto.ec2
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
		
		f = open(results+requestID+".xml","a+b")
		f.write(result)
		f.close()

		logger.info("Result written to %s" % xmltext)

		if not qOutgoing:
			qOutgoing = AWSSQS(FRONTEND_INCOMING)

		qOutgoing.write("http://%s/%s" % (public_ip(), requestID+".xml"))

		qIncoming.delete(m)
	except Exception, e:
		logger.error('Exception %s' % e)
		print e
		time.sleep(60)
