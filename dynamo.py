import boto
import time
import os
from boto.dynamodb.condition import *

user = os.environ['LTU_USER']

class db:
	def __init__(self):
		self.conn = boto.dynamodb.connect_to_region('eu-west-1')
		if not '12_LP1_DDB_D7001D_%s' % user in self.conn.list_tables():
			self.create_db()
		self.table = self.conn.get_table('12_LP1_DDB_D7001D_%s' % user)
	
	def load_packets(self, cell, side, cartype, start=0, end=2**64):
		items = self.table.query(
			hash_key=(cell << 40) + (side << 32) + cartype,
			range_key_condition = BETWEEN((start << 32), (end << 32) + 2**32),
		)
		ret = []
		for item in items:
			ret.append(item['data'])
		return ret
	
	def save_packet(self, cell, node, side, timestamp, cartype, data):
		attr = {
			'data':data,
		}
		
		item = self.table.new_item(
			hash_key=(cell << 40) + (side << 32) + cartype,
			range_key=(timestamp << 32) + node,
			attrs=attr
		)
		item.put()
	
	def create_db(self):
		schema = self.conn.create_schema(
			hash_key_name='cell_side_car',
			hash_key_proto_value=int,
			range_key_name='timestamp_node',
			range_key_proto_value=int
		)
		
		table = self.conn.create_table(
			name='12_LP1_DDB_D7001D_%s' % user,
			schema=schema,
			read_units=10,
			write_units=10
		)
		while not '12_LP1_DDB_D7001D_%s' % user in self.conn.list_tables():
			time.sleep(5)
	
