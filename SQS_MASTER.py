#!/usr/bin/python
import os, time
import logger
from AWSSQS import AWSSQS

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



def launch_instances(self, ami, num=1, extra_tags = {}):
	# Launch one or more EC2 instances from AMI
	res = self.conn.run_instances(
		image_id=ami,
		key_name='12_LP1_KEY_D7001D_%s' % user,
		instance_type='t1.micro',
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
		qtoken = AWSSQS(MASTER_TOKEN, create = False)
	if qin is None:
		qin = AWSSQS(FRONTEND_INCOMING, create = False)


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
				launch_instances(ami = GUI_AMI_WORKER, extra_tags = {'Frontend' : 'Worker'})
				logger.info("Instance launched")
				
				NUM_INSTANCES += 1
			elif length < NUM_INSTANCES * SQS_LIMIT_LOW:
				logger.info("Decreasing instances")

				# Remove instances by sending a message
				qin.write("STOPINSTANCE")
				NUM_INSTANCES -=1

			if c != 0:
				time.sleep(TOKEN_TIME) # So in total we wait TOKEN_TIME + INTERVALL meaning other guy(s) should have taken it on next run for sure if they are alive
			
			if c == 3: # We give up waiting and considering it dead
				launch_instances(ami = GUI_AMI_MASTER, num = 1, extra_tags = {'Frontend' : 'Master'})

			c +=1


	except Exception, e:
		# Always log exceptions
		logger.error('Exception %s' % e)
	
	time.sleep(INTERVALL)

