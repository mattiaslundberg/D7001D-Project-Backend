import boto
import boto.dynamodb
import time
import os
import base64
import logging
from settings import user
from exception import CellNotFoundError
from boto.dynamodb.condition import *

logger = logging.getLogger('db_data')
handler = logging.FileHandler('/tmp/db_data.log')
logger.addHandler(handler)
logger.setLevel(logging.INFO)

class db:
	def __init__(self):
		self.conn = boto.dynamodb.connect_to_region('eu-west-1')
		if not '12_LP1_DATA_D7001D_%s' % user in self.conn.list_tables():
			self.create_prim()
		self.table = self.conn.get_table('12_LP1_DATA_D7001D_%s' % user)
		
		if not '12_LP1_CELLS_D7001D_%s' % user in self.conn.list_tables():
			self.create_slave()
		self.cells = self.conn.get_table('12_LP1_CELLS_D7001D_%s' % user)
		
		while self.table.status != 'ACTIVE' and self.cells.status != 'ACTIVE':
			time.sleep(5)
			self.table.refresh()
			self.cells.refresh()
		logger.info('Inited databases')
	
	def load_packets(self, cell, side, cartype, start=0, end=2**64):
		logger.info('loading packet cell=%s side=%s car=%s interval=%s-%s',cell,side,cartype,start,end)
		cells = self.cells.query(hash_key=1, range_key_condition = EQ(cell))
		if not cell in self.load_cells():
			raise CellNotFoundError()
		items = self.table.query(
			hash_key=(cell << 40) + (side << 32) + cartype,
			range_key_condition = BETWEEN((start << 32), (end << 32) + 2**32),
		)
		ret = []
		for item in items:
			ret.append({'data':base64.b64decode(item['data']), 'timestamp':(item['timestamp_node'] >> 32)})
		return ret
	
	def save_packet(self, cell, node, side, timestamp, cartype, data):
		logger.info('saving packet  cell=%s node=%s side=%s time=%s car=%s',cell,node,side,timestamp,cartype)
		attr = {
			'data':base64.b64encode(data),
		}
		
		item = self.table.new_item(
			hash_key=(cell << 40) + (side << 32) + cartype,
			range_key=(timestamp << 32) + node,
			attrs=attr
		)
		item.put()
		
		items = self.cells.query(
			hash_key=1,
			range_key_condition=EQ(cell)
		)
		for it in items:
			return
		i = self.cells.new_item(hash_key=1, range_key=cell)
		i.put()
	
	def load_cells(self):
		cells = []
		items = self.cells.query(
			hash_key=1
		)
		for i in items:
			cells.append(i['cell_id'])
		return cells
	
	def create_prim(self):
		schema = self.conn.create_schema(
			hash_key_name='cell_side_car',
			hash_key_proto_value=int,
			range_key_name='timestamp_node',
			range_key_proto_value=int
		)
		
		table = self.conn.create_table(
			name='12_LP1_DATA_D7001D_%s' % user,
			schema=schema,
			read_units=10,
			write_units=10
		)
	
	def create_slave(self):
		schema = self.conn.create_schema(
			hash_key_name='nan',
			hash_key_proto_value=int,
			range_key_name='cell_id',
			range_key_proto_value=int
		)
		
		table = self.conn.create_table(
			name='12_LP1_CELLS_D7001D_%s' % user,
			schema=schema,
			read_units=10,
			write_units=10
		)
