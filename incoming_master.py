#!/usr/bin/python
import os, time
import logger
#import boto
#import boto.ec2
from threading import Thread
import urllib2
from awssqs import awssqs
import deploy
from settings import * # Global variables
import socket
TIMEOUT = max(INTERVALL - 10, 20)
socket.setdefaulttimeout(TIMEOUT)

SQS_LIMIT_LOW = 2
SQS_LIMIT_HIGH = 5
MIN_WORKERS = 1
MAX_WORKERS = 4

logger = logging.getLogger('SQSMASTER')
handler = logging.FileHandler('/tmp/SQSMASTER.log')
logger.addHandler(handler) 
logger.setLevel(logging.INFO)


qtoken = None
qin = None
connector = None
c = 0
result = {}

def getQ():
	if qtoken is None:
		qtoken = awssqs(MASTER_TOKEN)
	if qin is None:
		qin = awssqs(FRONTEND_INCOMING)
	if connector is None:
		connector = deploy.Connector()


def tryInstance(instance):
	global result # Dict for automatic lock
	success = False
	tries = 0
	addr = instance.public_dns_name
	while not success:
		try:
			f = urllib2.urlopen(addr, timeout = TIMEOUT)
			if f.read():
				success = True
				status = "OK"
			else:
				status = "BAD"
				tries +=1
				success = tries >= 3

			result[addr] = (instance, status)
		except Exception, e:
			info('Exception %s' % e)
			logger.error('Exception %s' % e)
			time.sleep(10)


def active_workers():
	result = {}
	instances = connector.get_instances({'tag-value':'Worker'})
	for instance in instances:
		t = Thread(target=tryInstance, args=(instance,))
        t.start()

def info(text):
	logger.info(text)
	print text

while True:
	try:
		getQ()
		m = qtoken.read()
		t = time.time()
		if m is None: # Someone else got token.
			c = 0
			info("Someone else got token")
		else:
			tokentext = m.get_body()

			# We got token now
			active_workers()
			time.sleep(TOKEN_TIME - (time.time() - t) - 10) # 10 seconds to actual do the start/stoping of workers

			num_good_workers = len([ instance for k, (instance, status) in result.iteritems() if status == 'OK' ])
			bad_workers = [ instance for k, (instance, status) in result.iteritems() if status == 'BAD' ]

			for bad_worker in bad_workers:
				info("stop worker %s" % bad_worker.public_dns_name)
				connector.stop_instance(bad_worker)

			qIn_len = qin.length()
			if qIn_len >= num_good_workers * SQS_LIMIT_HIGH and num_good_workers < MAX_WORKERS:
				# Launch instances
				info("Creating instances")
				connector.launch_instances(ami = GUI_AMI_WORKER, extra_tags = {'Frontend' : 'Worker'}, instance_type='m1.small')
				info("Instance launched")
				
			elif qIn_len < num_good_workers * SQS_LIMIT_LOW and num_good_workers > MIN_WORKERS:
				info("Decreasing instances")

				# Remove instances by sending a message
				# Meaning that we do not interrupt one.. 
				# else we could just pick a instance from the list with good workers and stop directly
				qin.write("STOPINSTANCE") 

			if c == 3: # We give up waiting and considering it dead
				connector.launch_instances(ami = GUI_AMI_MASTER, num = 1, extra_tags = {'Frontend' : 'Master'}, instance_type='m1.small')

			if c != 0:
				# In total we wait TOKEN_TIME + INTERVALL * 1.5  - 10(in worst case)
				# 0.5*INTERVALL to avoid race condition if they happend to be in sync in the first time
				time.sleep(INTERVALL*0.5)

			c +=1


	except Exception, e:
		info('Exception %s' % e)
		# Always log exceptions
		logger.error('Exception %s' % e)
	
	time.sleep(INTERVALL)
