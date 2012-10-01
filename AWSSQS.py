from boto.sqs.connection import SQSConnection
from boto.sqs.message import Message
import boto.sqs # Needed for boto.sqs.regions()

class AWSSQS:
	def __init__(self, name, create = False):
		self.conn = SQSConnection(region=boto.sqs.regions()[1])
		if create:
			self.q = self.conn.create_queue(name)
		else:
			self.q = self.conn.get_queue(name)
		
		if self.q is None:
			raise Exception("Could not get that queue " + name)

	def write(self, message):
		if self.q is None:
			raise Exception("Queue is none " + name)
		m = Message()
		m.set_body(message)
		success = self.q.write(m)
		while not success:
			success = q.write(m) # Keep trying until success

	# Return a Message, use m.get_body() to get text
	def read(self):
		if self.q is None:
			raise Exception("Queue is none " + name)
		rs = self.q.get_messages(visibility_timeout = 60)
		if len(rs) > 0:
			m = rs[0]
			return m
		return None

	def length(self):
		if self.q is None:
			raise Exception("Queue is none " + name)
		rs = self.q.get_messages(visibility_timeout = 60)
		return len(rs)


	def delete(self, m):
		self.q.delete_message(m)

	def deleteQueue(self):
		self.conn.delete_queue(self.q)
		self.q = None
