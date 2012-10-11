#!/usr/bin/python
import os, time
import logging
#import boto
#import boto.ec2
from threading import Thread
import urllib2
from awssqs import awssqs
from deploy import Connector
from settings import * # Global variables
import socket
TIMEOUT = max(INTERVALL - 10, 20)
socket.setdefaulttimeout(TIMEOUT)

SQS_LIMIT_LOW = 2
SQS_LIMIT_HIGH = 5
MIN_WORKERS = 1
MAX_WORKERS = 4

logger = logging.getLogger('incomming_master')
handler = logging.FileHandler('/tmp/in_master.log')
logger.addHandler(handler) 
logger.setLevel(logging.INFO)

#http://docs.amazonwebservices.com/AWSEC2/latest/UserGuide/AESDG-chapter-instancedata.html
AMAZON_META_DATA_URL_AMI_ID = "http://169.254.169.254/latest/meta-data/ami-id"

class master:

	qtoken = None
	qin = None
	connector = None
	ami_id = None
	c = 0
	result = {}

	def getQ(self):
		if self.qtoken is None:
			self.qtoken = awssqs(MASTER_TOKEN)
		if self.qin is None:
			self.qin = awssqs(FRONTEND_INCOMING)
		if self.connector is None:
			self.connector = Connector()


	def tryInstance(self, instance):
		#self.result # Dict for automatic lock
		success = False
		tries = 0
		addr = instance.public_dns_name
		while not success:
			try:
				f = urllib2.urlopen("http://%s:%s" % (addr, 80), timeout = TIMEOUT)
				if f.read():
					success = True
					status = "OK"
				else:
					status = "BAD"
					tries +=1
					success = tries >= 3

				self.result[addr] = (instance, status)
			except Exception, e:
				info('Exception %s' % e, error = True)
				time.sleep(10)


	def active_workers(self):
		self.result = {}
		instances = self.connector.get_instances({'tag-value':'Worker'})
		for instance in instances:
			if instance.state == u'running':
				t = Thread(target=self.tryInstance, args=(instance,))
				t.start()

	def AMI_ID(self):
		if not self.ami_id:
			success = False
			tries = 0
			while not success:
				try:
					f = urllib2.urlopen(AMAZON_META_DATA_URL_AMI_ID, timeout = 10)
					self.ami_id = f.read()
					tries +=1
					if self.ami_id:
						success = True
					else:
						success = tries >= 3
				except Exception,e:
					info("%s" % e, error = True)
					time.sleep(5)


	def __init__(self):
		while True:
			try:
				self.getQ()
				m = self.qtoken.read()
				t = time.time()
				if m is None: # Someone else got token.
					self.c = 0
					info("Someone else got token")
				else:
					info('i got token :)')
					tokentext = m.get_body()

					# We got token now
					self.active_workers()
					time.sleep(TOKEN_TIME - (time.time() - t) - 10) # 10 seconds to actual do the start/stoping of workers

					num_good_workers = len([ instance for k, (instance, status) in self.result.iteritems() if status == 'OK' ])
					bad_workers = [ instance for k, (instance, status) in self.result.iteritems() if status == 'BAD' ]

					for bad_worker in bad_workers:
						info("stop worker %s" % bad_worker.public_dns_name)
						self.connector.stop_instance(bad_worker)

					self.qin_len = self.qin.length()
					if self.qin_len >= num_good_workers * SQS_LIMIT_HIGH and num_good_workers < MAX_WORKERS:
						# Launch instances
						info("Creating instances")
						worker_ami = self.connector.get_ami(input_filter = {'tag-value' : 'Worker'})
						self.connector.launch_instances(ami = worker_ami, extra_tags = {'Frontend' : 'Worker'}, instance_type='m1.small')
						info("Instance launched")
						
					elif self.qin_len < num_good_workers * SQS_LIMIT_LOW and num_good_workers > MIN_WORKERS:
						info("Decreasing instances")

						# Remove instances by sending a message
						# Meaning that we do not interrupt one.. 
						# else we could just pick a instance from the list with good workers and stop directly
						self.qin.write("STOPINSTANCE") 

					if self.c >= 2: # We give up waiting and considering it dead after 3 tries
						info("Starting another MASTER")
						c = -1 # Cleared
						self.AMI_ID()
						self.connector.launch_instances(ami = self.ami_id, num = 1, extra_tags = {'Frontend' : 'Master'}, instance_type='m1.small')

					if self.c != 0:
						# In total we wait TOKEN_TIME + INTERVALL * 1.5  - 10(in worst case)
						# 0.5*INTERVALL to avoid race condition if they happend to be in sync in the first time
						time.sleep(INTERVALL*0.5)

					self.c +=1

			except Exception, e:
				info('Exception %s' % e, error = True)

			
			time.sleep(INTERVALL)


def info(text, error = False):
	if error:
		logger.error(text)
	else:
		logger.info(text)
	print text

if __name__ == "__main__":
	master()
