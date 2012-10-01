#!/usr/bin/python
import os, time
import logger
from AWSSQS import AWSSQS, length, write

GUI_AMI_WORKER = ''
SQS_LIMIT_LOW = 2
SQS_LIMIT_HIGH = 5
NUM_INSTANCES = 0
INTERVALL = 120

user = os.environ['LTU_USER']
FRONTEND_INCOMING = '12_LP1_SQS_D7001D_FRONTEND_INCOMING_%s' % user

logger = logging.getLogger('SQSMASTER')
handler = logging.FileHandler('/tmp/SQSMASTER.log')
logger.addHandler(handler) 
logger.setLevel(logging.INFO)

def launch_instances(self, ami, num=1, extra_tags = {}):
	# Launch one or more EC2 instances from AMI
	self.res = self.conn.run_instances(
		ami,
		key_name='12_LP1_KEY_D7001D_%s' % user,
		instance_type='c1.small',
		security_groups=['12_LP1_SEC_D7001D_%s' % user],
		min_count=num, max_count=num,monitoring_enabled=True,
		placement='eu-west-1a')

	# Tag instances
	for inst in self.res.instances:
		inst.add_tag('Name', '12_LP1_EC2_D7001D_%s' % user)
		inst.add_tag('user', user)
		inst.add_tag('course', 'D7001D')
		for key, value in extra_tags.items():				
			inst.add_tag(key, value)


while True:
	try:
		awssqs = AWSSQS(FRONTEND_INCOMING, create = False)
		length = awssqs.length()
		if length > NUM_INSTANCES * SQS_LIMIT_HIGH:
			# Launch instances
			logger.info("Creating instances")
			launch_instances(1, ami = GUI_AMI_WORKER, extra_tags = {'Frontend' : 'True', 'Worker' : 'True'})
			logger.info("Instance launched")
			
			NUM_INSTANCES += 1
		elif length < NUM_INSTANCES * SQS_LIMIT_LOW:

			# Remove instances by sending a message
			awssqs.write("STOPINSTANCE")
			NUM_INSTANCES -=1


	except Exception, e:
		# Always log exceptions
		logger.error('Exception %s' % e)
	
	time.sleep(INTERVALL)










