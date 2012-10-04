#!/usr/bin/python
import os, time
import logger
import boto
import boto.ec2
from awssqs import awssqs

GUI_AMI_WORKER = ''
GUI_AMI_MASTER = '' # TODO CHANGE!
SQS_LIMIT_LOW = 2
SQS_LIMIT_HIGH = 5
NUM_INSTANCES = 0
INTERVALL = 60
TOKEN_TIME = INTERVALL*4

user = os.environ['LTU_USER']
FRONTEND_INCOMING = '12_LP1_SQS_D7001D_FRONTEND_INCOMING_%s' % user
MASTER_TOKEN = "12_LP1_SQS_D7001D_FRONTEND_MASTER_%s" % user


logger = logging.getLogger('SQSMASTER')
handler = logging.FileHandler('/tmp/SQSMASTER.log')
logger.addHandler(handler) 
logger.setLevel(logging.INFO)

conn = boto.ec2.connect_to_region('eu-west-1')

def launch_instances(ami, num=1, extra_tags = {}, instance_type = "m1.small"):
	# Launch one or more EC2 instances from AMI
	res = conn.run_instances(
		image_id=ami,
		key_name='12_LP1_KEY_D7001D_%s' % user,
		instance_type=instance_type,
		security_groups=['12_LP1_SEC_D7001D_%s' % user],
		min_count=num, max_count=num,monitoring_enabled=True,
		placement='eu-west-1a')

	# Tag instances
	for inst in res.instances:
		inst.add_tag('Name', '12_LP1_EC2_D7001D_%s' % user)
		inst.add_tag('user', user)
		inst.add_tag('course', 'D7001D')
		for key, value in extra_tags.items():
			inst.add_tag(key, value)


qtoken = None
qin = None
c = 0

def getQ():
	if qtoken is None:
		qtoken = awssqs(MASTER_TOKEN, create = False)
	if qin is None:
		qin = awssqs(FRONTEND_INCOMING, create = False)


while True:
	try:
		getQ()
		m = qtoken.read()
		if m is None: # Someone else got token
			c = 0 
		else:
			tokentext = m.get_body()
			# We got token now			

			length = qin.length()
			if length >= NUM_INSTANCES * SQS_LIMIT_HIGH:
				# Launch instances
				logger.info("Creating instances")
				launch_instances(ami = GUI_AMI_WORKER, extra_tags = {'Frontend' : 'Worker'}, instance_type = "m1.small")
				logger.info("Instance launched")
				
				NUM_INSTANCES += 1
			elif length < NUM_INSTANCES * SQS_LIMIT_LOW:
				logger.info("Decreasing instances")

				# Remove instances by sending a message
				qin.write("STOPINSTANCE")
				NUM_INSTANCES -=1

			if c == 3: # We give up waiting and considering it dead
				launch_instances(ami = GUI_AMI_MASTER, num = 1, extra_tags = {'Frontend' : 'Master'}, instance_type='t1.micro')

			if c != 0:
				 # In total we wait TOKEN_TIME + INTERVALL + 10 meaning other guy(s) should have taken it on next run for sure if they are alive
				 # +10 tp avoid race condition if they happend to be in sync in the first time
				time.sleep(TOKEN_TIME+10)

			c +=1


	except Exception, e:
		# Always log exceptions
		logger.error('Exception %s' % e)
	
	time.sleep(INTERVALL)

