#!/usr/bin/env python

from openpyxl import load_workbook
from copy import copy


def get_style(cell):
	# WARNING:
	# FROM: https://stackoverflow.com/questions/23332259/copy-cell-style-openpyxl
	# cell.font or cell.border is an instance of StyleProxy
	# if save workbook with that type, you will get an exception. 
	# You must copy it to new cell, like this: new_cell.font = copy(cell.font)
	return {
		'font'          : copy(cell.font),
		'border'        : copy(cell.border),
		'fill'          : copy(cell.fill),
		'number_format' : copy(cell.number_format),
		'protection'    : copy(cell.protection),
		'alignment'     : copy(cell.alignment)
	}

def apply_style(cell, style_obj):
	cell.font          = style_obj['font']
	cell.border        = style_obj['border']
	cell.fill          = style_obj['fill']
	cell.number_format = style_obj['number_format']
	cell.protection    = style_obj['protection']
	cell.alignment     = style_obj['alignment']
	return cell

class ExcelTable():

	def __init__(self, path, sheet, START_ROW):
		self.wb = load_workbook(path)
		self.ws = self.wb[sheet]
		self.START_ROW = START_ROW

		self.ROW_TEMPLATE = []
		self.ROW_STYLE = []
		return

	# TODO Header

	#def set_validator(self, func):
	#	self.validator = func
	#	return self

	#def process(self, func):
	#	for i in range(RULE_BEGIN_ROW_INDEX, RBAC_RULE_CONF.nrows):
	#	self.postprocessor = func
	#	return self

	#def set_postprocessor(self, func):
	#	self.postprocessor = func
	#	return self

	#def read(self):
	#	self.postprocessor(row)
	#	for i in range(RULE_BEGIN_ROW_INDEX, RBAC_RULE_CONF.nrows):
	#		rule_row = map(lambda x: str(x.value).strip(), RBAC_RULE_CONF.row(i)[0:8])
	#		_area_flag, _exclusion_flag, _container_name, _db_name, _condition, _join_clause, _priority = rule_row
	#		### TODO implement excel interface here read string as it is
	#		if _join_clause == 'None':
	#			_join_clause = ''
	#		_lookup_tuple = (_area_flag.lower(), _exclusion_flag.lower())
	#		if _lookup_tuple not in RULE_DICT:
	#			RULE_DICT[_lookup_tuple] = []
	#		### WARNING: data type are all STRING
	#		RULE_DICT[_lookup_tuple].append({
	#			'container_name': _container_name,
	#			'db_name': _db_name,
	#			'condition': _condition,
	#			'join_clause': _join_clause,
	#			'priority': float(_priority)
	#		})


	def format(self, contexts, ENVIRONMENT):
		for cell in self.ws[self.START_ROW]:
			self.ROW_TEMPLATE.append(str(cell.value))
			self.ROW_STYLE.append(get_style(cell))
		for i, context in enumerate(contexts):
			for j in range(0, len(self.ROW_TEMPLATE)):
				#print(ROW_TEMPLATE[j].format(context))
				context['k'] = i+1
				# WARNING: Excel count 1,2,3,...
				_cell = self.ws.cell(row=self.START_ROW+i,column=j+1)
				_cell.value = self.ROW_TEMPLATE[j].format(**context)
				self.ws.row_dimensions[self.START_ROW+i+1].height = self.ws.row_dimensions[self.START_ROW].height
				apply_style(_cell, self.ROW_STYLE[j])
				#ws.cell(row=i,column=j,value=ROW_TEMPLATE[j].format(context)
		self.ws['A1'] = self.ws['A1'].value.format(ENVIRONMENT=ENVIRONMENT.upper().replace('DL',''))
		return self

	def save(self, filename):
		self.wb.save(filename)
		return self
