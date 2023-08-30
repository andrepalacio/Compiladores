from dataclasses import dataclass

@dataclass
class Node:
	pass

@dataclass
class Statement(Node):
	pass

@dataclass
class Expression(Node):
	pass

@dataclass
class Literal(Expression):
	'''
	Un valor literal como 2, 2.5, o "dos"z
	'''
	pass

@dataclass
class Location(Statement):
	pass

# Nodos Reales del AST
@dataclass
class Number(Literal):
	value : float

@dataclass
class Binop(Expression):
	'''
	Un operador binario como 2 + 3 o x * y
	'''
	op    : str
	left  : Expression
	right : Expression

@dataclass
class SimpleLocation(Location):
	name : str

@dataclass
class ReadLocation(Expression):
	location : Location

@dataclass
class WriteLocation(Statement):
	location : Location
	value    : Expression