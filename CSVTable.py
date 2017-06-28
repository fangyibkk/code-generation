#################################################################################################################
#   Name           : CSVTable.py
#   Requirement    : python 2
#   Purpose        : SQL like interface to CSV file
#################################################################################################################

from __future__ import print_function
from Predicate import Predicate
from datetime import datetime
from copy import copy
from pprint import pprint
from rbac_utils import group_by, get_rbac_db_name

import csv

class  CSVTable:

	def __init__(self, collections=[]):
		self.collections = collections
		self.cursor = copy(self.collections)
		# TODO add validate headings
		headings = []
		for collection in collections:
			if headings and headings != collection.keys():
				raise ValueError('inconsistence headings in collection supplied to CSVTable')
			headings = collection.keys()
		self.headings = headings
		return


	def _validate_file_obj(self, csv_file_obj):
		if not hasattr(csv_file_obj, 'read'):
			print('[ERROR] CSVTable.load argument: ', csv_file_obj)
			raise ValueError('Argument supplied to CSVTable is not an instance of File')
		return

	def _validate_in_headings(self, by):
		if by not in self.headings:
			raise SyntaxError('by argument %s supplied to "by" is not in headings' % by)

	def load(self, csv_file_obj):
		self._validate_file_obj(csv_file_obj)
		#f_csv = csv.reader(csv_file_obj)
		#self.headings = next(f_csv)
		reader = csv.DictReader(csv_file_obj)
		self.headings = reader.fieldnames
		self.collections = [row for row in reader]
		#print(self.collections[0:5])
		self.cursor = copy(self.collections)
		#print(self.collections)
		return self

	def where(self, where):
		cursor = []
		#print(columns)
		for row in self.cursor:
			if where(row):
				cursor.append(row)
		self.cursor = cursor
		return self

	def select(self, columns):
		cursor = []
		if columns == '*':
			columns = self.headings
		if isinstance(columns, str):
			columns = [columns]
		for row in self.cursor:
			selected_row = { column: row[column] for column in columns }
			cursor.append(selected_row)
		self.cursor = cursor
		self.headings = columns
		return self

	def transform(self, func):
		# WARNING this will not preserve data type as list of dictionary
		cursor = []
		for row in self.cursor:
			cursor.append(func(row))
		self.cursor = cursor
		return self

	def minus(self, table_b):
		# A-B in set theory
		cursor = []
		if self.headings != table_b.headings:
			raise ValueError('Cannot minus table with different headings')
		if not isinstance(table_b, CSVTable):
			raise ValueError('argument to CSVTable.minus should be an instance of CSVTable')
		print(len(self.cursor))
		print(len(table_b.cursor))
		for row_a in self.cursor:
			#for row_b in table_b.cursor:
				#if row_a['db_name'] == 'dluat_curated_fraud_db' and row_b['db_name'] == 'dluat_curated_fraud_db':
				#print(row_a)
				#print(row_b)
				#print(row_a == row_b)
			if row_a not in table_b.cursor:
				cursor.append(row_a)
		self.cursor = cursor
		print(len(self.cursor))
		return self

	def write(self, csv_file_obj):

		self._validate_file_obj(csv_file_obj)

		with csv_file_obj as f:
			f_csv = csv.DictWriter(f,
				self.headings, 
				lineterminator = '\n',
				quotechar = '"'
			)
			f_csv.writeheader()
			f_csv.writerows(self.cursor)

	def limit(self, num):
		self.cursor = self.cursor[0: num]
		return self

	def distinct(self):
		cursor = []
		for c in self.cursor:
			if c not in cursor: 
				cursor.append(c)
		self.cursor = cursor
		return self

	def sort_by(self, by):
		self._validate_in_headings(by)
		sort_key = sorted([k[by] for k in self.cursor])
		cursor = []
		for k in sort_key:
			#print(CSVTable(self.done()).done())
			cursor += CSVTable(self.done()).where(lambda row: row[by] == k).done()
		self.cursor = cursor
		return self

	### METHOD BELOW DO NOT RETURN CSVTable INSTANCE

	def done(self):
		return copy(self.cursor)

	def get_distinct(self, field):
		distinct = self.select(field).distinct().transform(lambda row: row[field]).done()
		if len(distinct) != 1:
			raise ValueError('query field %s has number of value other than 1' % field)
		return distinct[0]

	def first(self):
		return copy(self.cursor[0])

	def key_by(self, by, field=None):
		# TODO by not in self.header raise exception
		self._validate_in_headings(by)
		dt = {}
		for collection in self.cursor:
			if field:
				selected = collection[field]
			else:
				selected = collection
			if collection[by] in dt.keys():
				dt[collection[by]].append(selected)
			else:
				dt[collection[by]] = [selected]
		return dt
	
if __name__ == '__main__':

	table_filter_specs = CSVTable().load(open('./maintain/table_filter_spec.csv', 'rU')).done()

	def set_no_record_h(row):
		if row['combined_cond'] == 'no record':
			row['combined_cond'] = 'TRUE'
		return row
	result2 = CSVTable(table_filter_specs).where(lambda x: x['container_name']=='dep_acct_prod').get_distinct('db_name')
	assert(result2 == '${var:environment}_curated_dep_db')
	#csv_table = CSVTable().load(open('./maintain/table_filter_spec.csv', 'rU'))\
	#		.select('*', where=lambda row: row['container_name'] == 'dep_item' and row['access_level'] == 'H')\
	#		.transform(set_no_record_h)\
	#		.key_by('access_level')
	csv_table = CSVTable(table_filter_specs)\
			.where(lambda row: row['container_name'] == 'dep_item')\
			.where(lambda row: row['access_level'] == 'C')\
			.where(lambda row: row['combined_cond'] != 'no record')\
			.transform(set_no_record_h)\
			.key_by('access_level')
	#pprint(csv_table)
