
#################################################################################################################
#   Name           : Predicate.py
#   Requirement    : python 2
#   Purpose        : Share python class that are used across rbac script to reduce redundancy
#################################################################################################################

from __future__ import print_function

class Predicate:
	'''
	Explaination:
		Predicate class models SQL predicate
		this class only support strin generation and concaternation
		on other word this is just simple rendering engine
	Example:
		Predicate(*list, operator='AND', sep='\n')
		Predicate(pred1, pred2, pred3, operator='OR', sep='\n')
		Predicate('a=1','b=2',operator='AND').render()
		# a=1 AND b=2
	Properties:
		Only some property implemented
		(/) Predicate(*[]).render() must be ''
		(/) Predicate('').render() must be ''
		(/) p.AND, p.OR supports multiple arguments
		(/) We handle mixed operator in this way
		(/) identity:        x v 0 = x, x ^ 1 = x
		(/) annihilator:     x ^ 0 = 0
		but rather a v b v c ^ d => (a v b v c) ^ d

		In short, no Boolean algebra here. I mean:
		(X) absorption:      x ^ (x v y) = x, x v (x ^ y) = x
		(X) distributivity:  x v (y ^ z) = (x v y) ^ (y v z)
		'''
	def __init__(self, *preds, **opts):
		# preds is tuple
		# opts is an optional argument pass by name
		self.preds = list(preds)
		self.sep = opts.get('sep', '\n')
		self.operator = opts.get('operator', '')

	def _operate(self, preds, operator):
		if len(preds) == 1 and preds[0] == '':
			pass
		elif len(self.preds) > 1 and self.operator != operator:
			self.preds = [self.render(is_encapsulate=True)]
			self.operator = ''
			self._operate(preds, operator=operator)
		else:
			self.set_operator(operator)
			self.preds += preds
			#self.preds.append(pred)
		return self

	def AND(self, *preds):
		# Identity
		if 'TRUE' in preds:
			preds = set(preds) - set(['TRUE'])
			self._operate(list(preds), operator='AND')
		elif 'FALSE' in preds:
			self.preds = ['FALSE']
			self.sep = '\n'
			self.operator = ''
		else:
			self._operate(list(preds), operator='AND')
		return self

	def OR(self, *preds):
		# Identity
		if 'FALSE' in preds:
			preds = set(preds) - set(['FALSE'])
			self._operate(list(preds), operator='OR')
		elif 'TRUE' in preds:
			self.preds = ['TRUE']
			self.sep = '\n'
			self.operator = ''
		else:
			self._operate(list(preds), operator='OR')
		return self

	def set_operator(self, operator):
		# WARNING: only one operator
		# because has no associative prop
		# e.g. A and B or C cannot be calculated
		#if self.operator != '' and self.operator != operator and len(self.preds) != 1:
		#	# case for single element array ([1], operator=AND)
		#	raise SyntaxError('only one operator (AND, OR) on one predicate')
		self.operator = operator 
		return self

	def render(self, is_encapsulate=False, sep=None):
		sep = self.sep if sep is None else sep
		# This method convert the Predicate to string

		if len(self.preds) > 1 and self.operator == '':
			print(self.preds)
			raise SyntaxError('No operator for multiple predicates')

		_seperator = ' ' + sep + self.operator + ' '
		if is_encapsulate:
			return ('(' + _seperator.join(self.preds) + ')').strip()
		return _seperator.join(self.preds).strip()

if __name__ == '__main__':

	print('[INFO] Test Predicate class')

	p = {} 
	p[0] = Predicate(*[]).render() 
	p[1] = Predicate('').render()
	p[3] = Predicate('a!=5').AND('b>2').AND('c<10').render(sep='')
	p[4] = Predicate('a!=5').AND('b>2').AND('c<10').OR('d%2==0').render()
	p[5] = Predicate('a!=5', 'b>2', 'c<10', operator='AND').render(is_encapsulate=True)
	p[6] = Predicate(*['a!=5', 'b>2', 'c<10'], operator='AND').render(is_encapsulate=True)
	p[7] = Predicate(*['a!=5', 'b>2'], operator='AND').OR('c<10', 'd%2==0').render()
	p[8] = Predicate(*['a!=5', 'b>2'], operator='AND').OR(*['c<10', 'd%2==0']).render()
	p[9] = Predicate(*['a!=5', 'b>2'], operator='AND') \
	.OR(Predicate(*['c<10', 'd%2==0'], operator='AND') \
	.render(is_encapsulate=True)).render()
	p[10] = Predicate('a!=5').OR('TRUE').render()
	p[11] = Predicate('a!=5').OR(*['FALSE','b>5']).render()
	p[12] = Predicate('a!=5').AND(*['TRUE','b>5']).render()
	p[13] = Predicate('a!=5').AND('FALSE').render(is_encapsulate=True)

	for key, val in p.iteritems():
		print('Item %i:\n%s\n' % (key, val))

	assert(p[0] == '')
	assert(p[1] == '')
	assert(p[3] == 'a!=5 AND b>2 AND c<10')
	assert(p[4].replace('\n','') == '(a!=5 AND b>2 AND c<10) OR d%2==0')
	assert(p[5].replace('\n','') == '(a!=5 AND b>2 AND c<10)')
	assert(p[6] == p[5])
	assert(p[7].replace('\n','') == '(a!=5 AND b>2) OR c<10 OR d%2==0')
	assert(p[8] == p[7])
	assert(p[9].replace('\n','') == '(a!=5 AND b>2) OR (c<10 AND d%2==0)')
	assert(p[10] == 'TRUE')
	assert(p[11].replace('\n','') == 'a!=5 OR b>5')
	assert(p[12].replace('\n','') == 'a!=5 AND b>5')
	assert(p[13] == 'FALSE')
	
	print('[INFO] Pass all assertation')
