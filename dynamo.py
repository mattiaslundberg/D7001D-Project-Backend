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
		time.sleep(5)
		self.table = self.conn.get_table('12_LP1_DDB_D7001D_%s' % user)
	
	def load_packets(self, cell, node, side, cartype, start=0, end=4294967296):
		items = self.table.query(
			hash_key=cell,
			range_key_condition = BETWEEN(start, end),
		)
		ret = []
		for item in items:
			if cell == item['cell_id'] and side == item['side'] and cartype == item['cartype']:
				ret.append(item['data'])
		return ret
	
	def save_packet(self, cell, node, side, timestamp, cartype, data):
		attr = {
			'cartype':cartype,
			'node':node,
			'side':side,
			'data':data,
		}
		
		item = self.table.new_item(
			hash_key=cell,
			range_key=timestamp,
			attrs=attr
		)
		item.put()
	
	def create_db(self):
		schema = self.conn.create_schema(
			hash_key_name='cell_id',
			hash_key_proto_value=int,
			range_key_name='timestamp',
			range_key_proto_value=int
		)
		
		table = self.conn.create_table(
			name='12_LP1_DDB_D7001D_%s' % user,
			schema=schema,
			read_units=10,
			write_units=10
		)
	
