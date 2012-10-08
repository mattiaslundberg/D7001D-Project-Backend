#!/usr/bin/python

import os
import boto
import boto.ec2
import boto.dynamodb
import time
import commands
from boto.ec2.elb import HealthCheck
from boto.ec2.autoscale import LaunchConfiguration
from boto.ec2.autoscale import AutoScalingGroup
from boto.ec2.autoscale import AutoScaleConnection, ScalingPolicy
from boto.ec2.cloudwatch import MetricAlarm
from boto.ec2.autoscale.tag import Tag
import boto.ec2.cloudwatch

from awssqs import awssqs
from settings import * # Global variables

class Connector():
	def __init__(self):
		self.connect()
	
	def connect(self):
		# Init needed connections
		self.conn = boto.ec2.connect_to_region('eu-west-1')
		self.elbconn = boto.ec2.elb.connect_to_region('eu-west-1')
		self.cwconn = boto.connect_cloudwatch(region=boto.ec2.cloudwatch.regions()[2])
		self.sconn = AutoScaleConnection(region=boto.ec2.autoscale.regions()[2])
	
	def launch_instances(self, ami, num=1, extra_tags = {}, instance_type = "m1.small"):
		# Launch one or more EC2 instances from AMI
		self.res = self.conn.run_instances(
			image_id=ami,
			key_name='12_LP1_KEY_D7001D_%s' % user,
			instance_type=instance_type,
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
	
	def stop_wsn(self):
		## Delete all things created
		try:
			self.elbconn.delete_load_balancer(WSN_ELB)
		except Exception, e:
			print e
		try:
			self.sconn.delete_auto_scaling_group(WSN_ASG, force_delete=True)
		except Exception, e:
			print e
		try:
			self.sconn.delete_launch_configuration(WSN_LC)
		except Exception, e:
			print e
		try:
			self.cwconn.delete_alarms([WSN_SCALE_DOWN, WSN_SCALE_UP])
		except Exception, e:
			print e
	
	def stop_gui(self):
		try:
			self.qout.deleteQueue()
		except Exception, e:
			print e

		try:
			self.qin.deleteQueue()
		except Exception, e:
			print e
		try:
			self.qtoken.deleteQueue()
		except Exception, e:
			print e

		# ELB and autoscale
		try:
			self.elbconn.delete_load_balancer(FRONTEND_ELB)
		except Exception, e:
			print e
		try:
			self.sconn.delete_auto_scaling_group(FRONTEND_ASG, force_delete=True)
		except Exception, e:
			print e
		try:
			self.sconn.delete_launch_configuration(FRONTEND_LC)
		except Exception, e:
			print e
		try:
			self.cwconn.delete_alarms([FRONTEND_SCALE_DOWN, FRONTEND_SCALE_UP])
		except Exception, e:
			print e
	
	def stop_db(self):
		dbconn = boto.dynamodb.connect_to_region('eu-west-1')
		try:
			tb = dbconn.get_table('12_LP1_DATA_D7001D_%s' % user)
			tb.delete()
		except Exception, e:
			print e
		try:
			tb = dbconn.get_table('12_LP1_CELLS_D7001D_%s' % user)
			tb.delete()
		except Exception, e:
			print e
		try:
			tb= dbconn.get_table('12_LP1_CALC_D7001D_%s' % user)
			tb.delete()
		except Exception, e:
			print e
		
	
	def stop_all(self):
		self.stop_instances()
		self.stop_wsn()
		self.stop_gui()

		self.conn.close()
	
	def stop_instances(self):
		# Stop all of my running instances and mark for deletion
		for r in self.conn.get_all_instances(filters={'tag-value':user}):
			for i in r.instances:
				if i.state == u'running':
					i.stop()
				i.add_tag('Name', 'delete-me_%s' % user)
				i.add_tag('action', 'delete')
	
	def print_ip(self):
		# Print IP:s I might need
		for e in self.elbconn.get_all_load_balancers():
			print 'ELB: %s' % e.dns_name
		for r in self.conn.get_all_instances(filters={'tag-value':user}):
			for i in r.instances:
				if i.state == u'running':
					print 'Instance: %s' % i.public_dns_name
	
	def start_wsn(self):
		# Launch a ELB with autoscaling
		ports = [(12345, 12345, 'tcp')]
		self.lb = self.elbconn.create_load_balancer(WSN_ELB, ['eu-west-1a'], ports)
		
		# DEF Healthcheck
		hc = HealthCheck(
			interval=20,
			healthy_threshold=3,
			unhealthy_threshold=5,
			target='TCP:12345'
		)
		
		self.lb.configure_health_check(hc)
		
		# Settings for launched instances
		self.lc = LaunchConfiguration(name=WSN_LC, image_id=WSN_AMI,
				key_name='12_LP1_KEY_D7001D_%s' % user,
				instance_type='m1.medium',
				security_groups=['12_LP1_SEC_D7001D_%s' % user])
		self.sconn.create_launch_configuration(self.lc)
		
		## Scale group
		self.ag = AutoScalingGroup(group_name=WSN_ASG, load_balancers=[WSN_ELB],
				availability_zones=['eu-west-1a'],
				launch_config=self.lc, min_size=2, max_size=8)
		self.sconn.create_auto_scaling_group(self.ag)
		
		# Tag instances
		ntag = Tag(key='Name', value='12_LP1_EC2_D7001D_%s' % user, resource_id=WSN_ASG,
			propagate_at_launch=True)
		ctag = Tag(key='course', value='D7001D', resource_id=WSN_ASG,
			propagate_at_launch=True)
		utag = Tag(key='user', value=user, resource_id=WSN_ASG,
			propagate_at_launch=True)
		self.sconn.create_or_update_tags([ntag,ctag,utag])
		
		# How to scale
		scale_up_policy = ScalingPolicy(
				name=WSN_POLICY_UP, adjustment_type='ChangeInCapacity',
				as_name=WSN_ASG, scaling_adjustment=1, cooldown=30)
		scale_down_policy = ScalingPolicy(
				name=WSN_POLICY_DOWN, adjustment_type='ChangeInCapacity',
				as_name=WSN_ASG, scaling_adjustment=-1, cooldown=30)
		
		self.sconn.create_scaling_policy(scale_up_policy)
		self.sconn.create_scaling_policy(scale_down_policy)
		
		scale_up_policy = self.sconn.get_all_policies(
			as_group=WSN_ASG, policy_names=[WSN_POLICY_UP])[0]
		scale_down_policy = self.sconn.get_all_policies(
			as_group=WSN_ASG, policy_names=[WSN_POLICY_DOWN])[0]
		
		# When to scale
		alarm_dimensions = {"AutoScalingGroupName": WSN_ASG}
		
		scale_up_alarm = MetricAlarm(
			name=WSN_SCALE_UP, namespace='AWS/EC2',
			metric='CPUUtilization', statistic='Average',
			comparison='>', threshold='60',
			period='60', evaluation_periods=2,
			alarm_actions=[scale_up_policy.policy_arn],
			dimensions=alarm_dimensions)
		self.cwconn.create_alarm(scale_up_alarm)
		scale_up_alarm.enable_actions()
		
		scale_down_alarm = MetricAlarm(
			name=WSN_SCALE_DOWN, namespace='AWS/EC2',
			metric='CPUUtilization', statistic='Average',
			comparison='<', threshold='40',
			period='60', evaluation_periods=2,
			alarm_actions=[scale_down_policy.policy_arn],
			dimensions=alarm_dimensions)
		self.cwconn.create_alarm(scale_down_alarm)
		scale_down_alarm.enable_actions()
	
	def start_gui(self):
		# SQS
		self.qin = awssqs(FRONTEND_INCOMING, create = True)
		self.qout = awssqs(FRONTEND_OUTGOING, create = True)
		self.qtoken = awssqs(MASTER_TOKEN, create = True, visibility_timeout = TOKEN_TIME)
		self.qtoken.write("token")

		self.launch_instances(ami = GUI_AMI_MASTER, num = 1, extra_tags = {'Frontend' : 'Master'}, instance_type='t1.micro')

		# ELB with autoscale
		ports = [(80, 80, 'http')]
		self.lb = self.elbconn.create_load_balancer(FRONTEND_ELB, ['eu-west-1a'], ports)
		
		# DEF Healthcheck
		hc = HealthCheck(
			interval=20,
			healthy_threshold=3,
			unhealthy_threshold=5,
			target='HTTP:80/'
		)
		
		self.lb.configure_health_check(hc)
		
		# Settings for launched instances
		self.lc = LaunchConfiguration(name=FRONTEND_LC, image_id=FRONTEND_HTTP_AMI,
				key_name='12_LP1_KEY_D7001D_%s' % user,
				instance_type='t1.micro',
				security_groups=['12_LP1_SEC_D7001D_%s' % user])
		self.sconn.create_launch_configuration(self.lc)
		
		## Scale group
		self.ag = AutoScalingGroup(group_name=FRONTEND_ASG, load_balancers=[FRONTEND_ELB],
				availability_zones=['eu-west-1a'],
				launch_config=self.lc, min_size=2, max_size=8)
		self.sconn.create_auto_scaling_group(self.ag)
		
		# Tag instances
		ntag = Tag(key='Name', value='12_LP1_EC2_D7001D_%s' % user, resource_id=FRONTEND_ASG,
			propagate_at_launch=True)
		ctag = Tag(key='course', value='D7001D', resource_id=FRONTEND_ASG,
			propagate_at_launch=True)
		utag = Tag(key='user', value=user, resource_id=FRONTEND_ASG,
			propagate_at_launch=True)
		ftag = Tag(key='FRONTEND', value="HTTP_WORKER", resource_id=FRONTEND_ASG,
			propagate_at_launch=True)
		self.sconn.create_or_update_tags([ntag,ctag,utag,ftag])
		
		# How to scale
		scale_up_policy = ScalingPolicy(
				name=FRONTEND_POLICY_UP, adjustment_type='ChangeInCapacity',
				as_name=FRONTEND_ASG, scaling_adjustment=1, cooldown=30)
		scale_down_policy = ScalingPolicy(
				name=FRONTEND_POLICY_DOWN, adjustment_type='ChangeInCapacity',
				as_name=FRONTEND_ASG, scaling_adjustment=-1, cooldown=30)
		
		self.sconn.create_scaling_policy(scale_up_policy)
		self.sconn.create_scaling_policy(scale_down_policy)
		
		scale_up_policy = self.sconn.get_all_policies(
			as_group=FRONTEND_ASG, policy_names=[FRONTEND_POLICY_UP])[0]
		scale_down_policy = self.sconn.get_all_policies(
			as_group=FRONTEND_ASG, policy_names=[FRONTEND_POLICY_DOWN])[0]
		
		# When to scale
		alarm_dimensions = {"AutoScalingGroupName": FRONTEND_ASG}
		
		scale_up_alarm = MetricAlarm(
			name=FRONTEND_SCALE_UP, namespace='AWS/EC2',
			metric='CPUUtilization', statistic='Average',
			comparison='>', threshold='60',
			period='60', evaluation_periods=2,
			alarm_actions=[scale_up_policy.policy_arn],
			dimensions=alarm_dimensions)
		self.cwconn.create_alarm(scale_up_alarm)
		scale_up_alarm.enable_actions()
		
		scale_down_alarm = MetricAlarm(
			name=FRONTEND_SCALE_DOWN, namespace='AWS/EC2',
			metric='CPUUtilization', statistic='Average',
			comparison='<', threshold='40',
			period='60', evaluation_periods=2,
			alarm_actions=[scale_down_policy.policy_arn],
			dimensions=alarm_dimensions)
		self.cwconn.create_alarm(scale_down_alarm)
		scale_down_alarm.enable_actions()
	
	def upload_code(self):
		for r in self.conn.get_all_instances(filters={'tag-value':user}):
			for i in r.instances:
				if i.state == u'running':
					print 'Deploying code to %s.' % i.public_dns_name
					my_key="-i $HOME/.ssh/12_LP1_KEY_D7001D_%s.pem" % user
					md="ssh -C -o StrictHostKeyChecking=no -Y %s ubuntu@%s" % (my_key, i.public_dns_name)
					
					print commands.getoutput('scp -o StrictHostKeyChecking=no %s * ubuntu@%s:~/' % (my_key, i.public_dns_name))
					print commands.getoutput('%s sudo chmod +x *' % (md) )


if __name__ == '__main__':
	c = Connector()
	c.start_wsn()
	#c.start_gui()
	time.sleep(30)
	c.print_ip()
	#time.sleep(10)
	#c.upload_code()
