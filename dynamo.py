import boto
import os
from boto.dynamodb.condition import *

user = os.environ['LTU_USER']

class db(Object):
	def __init__(self):
		self.conn = boto.dynamodb.connect_to_region('eu-west-1')
		if not '12_LP1_DB_D7001D_%s' % user in conn.list_tables():
			self.create_db()
		self.table = conn.get_table('12_LP1_DB_D7001D_%s' % user)
	
	def load_packets(self, cell, node, side, cartype, start=0, end=float('inf')):
		items = self.table.query(
			hash_key=cell,
			range_key_condition = BETWEEN(start, end),
		)
	
	def save_packet(self, cell, node, side, timestamp, cartype):
		attr = {
			'cartype':cartype,
			'node':node,
			'side':side,
		}
		
		item = self.table.new_item(
			hash_key=cell,
			range_key=timestamp,
			attrs=attr
		)
		item.put()
	
	def create_db(self):
		schema = conn.create_schema(
			hash_key_name='cell_id',
			hash_key_proto_value='S',
			range_key_name='timestamp',
			range_key_proto_value='S'
		)
		
		table = conn.create_table(
			name='12_LP1_DB_D7001D_%s' % user,
			schema=schema,
			read_units=10,
			write_units=10
		)
	
