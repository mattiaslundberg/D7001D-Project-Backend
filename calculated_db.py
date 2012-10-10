import boto
import time
import os
from boto.dynamodb.condition import *
from settings import user

class db:
	def __init__(self):
		self.conn = boto.dynamodb.connect_to_region('eu-west-1')
		if not '12_LP1_CALC_D7001D_%s' % user in self.conn.list_tables():
			self.create_db()
		self.table = self.conn.get_table('12_LP1_CALC_D7001D_%s' % user)
		while self.table.status != 'ACTIVE':
			time.sleep(5)
			self.table.refresh()
	
	def read(self, _id):
		item = self.table.get_item(hash_key=_id)
		
		for i in item:
			return item['data']
		return None
	
	def write(self, _id, data):
		attr = {
			'data':str(data),
		}
		
		item = self.table.new_item(
			hash_key=int(_id),
			attrs=attr
		)
		item.put()
	
	def create_db(self):
		schema = self.conn.create_schema(
			hash_key_name='idhash',
			hash_key_proto_value=int
		)
		
		self.table = self.conn.create_table(
			name='12_LP1_CALC_D7001D_%s' % user,
			schema=schema,
			read_units=10,
			write_units=10
		)
