import boto
import time
import os
from boto.dynamodb.condition import *

user = os.environ['LTU_USER']

class db:
	def __init__(self):
		self.conn = boto.dynamodb.connect_to_region('eu-west-1')
		if not '12_LP1_CALC_D7001D_%s' % user in self.conn.list_tables():
			self.create_db()
		self.table = self.conn.get_table('12_LP1_CALC_D7001D_%s' % user)
	
	def load_packets(self, _id):
		item = self.table.query(hash_key=_id)
		
		if len(item) > 0:
			return None
		return item['data']
		
	
	def save_packet(self, _id, data):
		attr = {
			'data':data,
		}
		
		item = self.table.new_item(
			hash_key=_id,
			attrs=attr
		)
		item.put()
	
	def create_db(self):
		schema = self.conn.create_schema(
			hash_key_name='idhash',
			hash_key_proto_value=int
		)
		
		table = self.conn.create_table(
			name='12_LP1_CALC_D7001D_%s' % user,
			schema=schema,
			read_units=10,
			write_units=10
		)
		
		while not '12_LP1_CALC_D7001D_%s' % user in self.conn.list_tables():
			time.sleep(5)
	
