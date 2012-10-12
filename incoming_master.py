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

SQS_LIMIT_LOW = 4
SQS_LIMIT_HIGH = 8
MIN_WORKERS = 1
MAX_WORKERS = 4

logger = logging.getLogger('incomming_master')
handler = logging.FileHandler('/tmp/in_master.log')
logger.addHandler(handler) 
logger.setLevel(logging.INFO)

#http://docs.amazonwebservices.com/AWSEC2/latest/UserGuide/AESDG-chapter-instancedata.html
AMAZON_META_DATA_URL_AMI_ID = "http://169.254.169.254/latest/meta-data/ami-id"
AMAZON_META_DATA_URL_INSTANCE_ID = "http://169.254.169.254/latest/meta-data/instance-id"

class master:

	qtoken = None
	qin = None
	connector = None
	ami_id = None
	c = 0
	result = {}
	masterdict = {}
	token = False
	started = False
	masterError = 0
	instance_id  = None
	tries = 3

	def getQ(self):
		if self.qtoken is None:
			self.qtoken = awssqs(MASTER_TOKEN)
		if self.qin is None:
			self.qin = awssqs(FRONTEND_INCOMING)
		if self.connector is None:
			self.connector = Connector()


	def tryInstance(self, instance, usemasterdict = False):
		success = False
		tries = 0
		addr = instance.public_dns_name
		info("Testing %s" % addr)
		url = "http://%s:%s" % (addr, 80)
		while not success:
			try:
				try:
					t = time.time()
					f = urllib2.urlopen(url, timeout = TIMEOUT)
				except Exception,e:
					status = "BAD"
					tries +=1
					success = tries >= self.tries
					r = (instance, status)

					if usemasterdict:
						self.masterdict[addr] = r
					else:
						self.result[addr] = r

					info("That was for url %s" % url)
					time.sleep(max(0,TIMEOUT - (time.time() - t)))
					continue

				if f.read():
					success = True
					status = "OK"
					info("url %s is ok" % url)
				else:
					status = "BAD"
					tries +=1
					success = tries >= self.tries

				r = (instance, status)

				if usemasterdict:
					self.masterdict[addr] = r
				else:
					self.result[addr] = r
			except Exception, e:
				info("Exception %s" % e, error = True)
				info("That was for url %s" % url)
				time.sleep(max(0,TIMEOUT - (time.time() - t)))


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
						success = tries >= self.tries
				except Exception,e:
					info("Problem with getting ami id: %s" % e, error = True)
					time.sleep(5)

	def get_instance_id(self):
		if not self.instance_id:
			f = urllib2.urlopen(AMAZON_META_DATA_URL_INSTANCE_ID, timeout = 10)
			self.instance_id = f.read()

	def handleMaster(self):
		info("handleMaster")
		self.masterdict = {}
		self.get_instance_id()
		instances = self.connector.get_instances({'tag-value':'Master'})
		for instance in instances:
			if instance.state == u'running' and instance.id != self.instance_id:
				# Got other master 
				t = Thread(target=self.tryInstance, args=(instance, True,))
				t.start()
				break

	def masterChecking(self, async = False):
		info("masterChecking called")
		loop = True
		while loop:
			if not async:
				loop = False

			if async:
				info("masterChecking with async")
			try:
				self.handleMaster()
				info("Wait for result...")
				time.sleep(self.tries * TIMEOUT)
				masterOK = 0 < len([ instance for k, (instance, status) in self.masterdict.iteritems() if status == 'OK' ])
				if masterOK:
					info("Master ok")
					self.masterError = 0
				else:
					# Master not ok
					info("Master not ok")
					self.masterError += 1
					if self.masterError == 3:
						# Should only be one, and if not we close them anyway
						bad_masters = [ instance for k, (instance, status) in self.masterdict.iteritems() if status == 'BAD' ]
						for bad_master in bad_masters:
							info("stop master %s" % bad_master.public_dns_name)
							try:
								self.connector.stop_instance(bad_master)
							except:
								pass # Dunno if this is needed but will continue close other master if multiple

						self.token = True
						self.masterError = 0

						info("Starting another MASTER")

						self.AMI_ID()
						self.connector.launch_instances(ami = self.ami_id, num = 1, extra_tags = {'Frontend' : 'Master'}, instance_type='m1.small')
						time.sleep(60) # Time to start
			except Exception, e:
				info("Exception %s" % e, error = True)
				time.sleep(10)


	def __init__(self):
		while True:
			try:
				self.getQ()

				if not self.token:
					self.masterChecking(async = False)
					info("I dont have token")
					continue
				elif not self.started:
					info("Master checking with async = True")
					t = Thread(target=self.masterChecking, args=(True,))
					t.start()
					self.started = True

				info("I got token, i rule!")

				self.active_workers()
				info("tests started")
				time.sleep(self.tries*TIMEOUT)

				num_good_workers = len([ instance for k, (instance, status) in self.result.iteritems() if status == 'OK' ])
				bad_workers = [ instance for k, (instance, status) in self.result.iteritems() if status == 'BAD' ]

				info("num_good_workers %s" % num_good_workers)
				info("num_bad_workers %s" % len(bad_workers))
				info(self.result)

				for bad_worker in bad_workers:
					info("stop worker %s" % bad_worker.public_dns_name)
					self.connector.stop_instance(bad_worker)

				self.qin_len = self.qin.length()
				if self.qin_len >= num_good_workers * SQS_LIMIT_HIGH and num_good_workers < MAX_WORKERS:
					# Launch instances
					info("Creating instances")

					worker_ami = self.connector.get_ami(input_filter = {'tag-value' : 'Worker'})
					self.connector.launch_instances(ami = worker_ami, num = 1, extra_tags = {'Frontend' : 'Worker'}, instance_type='m1.small')
					info("Instance launched")
					time.sleep(60) # Time to stop
					
				elif self.qin_len < num_good_workers * SQS_LIMIT_LOW and num_good_workers > MIN_WORKERS:
					info("Decreasing instances")

					# Remove instances by sending a message
					# Meaning that we do not interrupt one.. 
					# else we could just pick a instance from the list with good workers and stop directly
					self.qin.write("STOPINSTANCE") 
					time.sleep(60) # Time to start


			except Exception, e:
				info('Exception %s' % e, error = True)
				time.sleep(INTERVALL)


def info(text, error = False):
	text = "%s %s" % (time.ctime(), text)
	if error:
		logger.error(text)
	else:
		logger.info(text)
	print text

if __name__ == "__main__":
	master()
