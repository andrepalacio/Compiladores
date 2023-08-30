# model.py
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


# from dataclasses import dataclass

import re

# =======================================
# ANALISIS LEXICO
# =======================================
@dataclass
class Token:
	'''
	Representacion de un token
	'''
	type  : str
	value : float or str
	lineno: int = 1


class Tokenizer:
	
	tokens = [
		(r'\s+', None),
		(r'\d+(\.\d+)?(E[-+]?\d+)?', lambda s,tok:Token('NUMBER',tok)),
		(r'[a-zA-Z_]\w*',            lambda s,tok:Token('IDENT',tok)),
		(r'\+',                      lambda s,tok:Token('+',tok)),
		(r'-',                       lambda s,tok:Token('-',tok)),
		(r'\*',                      lambda s,tok:Token('*',tok)),
		(r'/',                       lambda s,tok:Token('/',tok)),
		(r'=',                       lambda s,tok:Token('=',tok)),
		(r'.',                       lambda s,tok:print("Error: caracter ilegal '%s'" % tok))]

	def tokenizer(self, text):
		scanner = re.Scanner(self.tokens)
		results, remainder = scanner.scan(text)

		return iter(results)

# =======================================
# ANALISIS SINTACTICO
# =======================================
# Recursive Descent Parser.
#
class RecursiveDescentParser(object):
	'''
	Implementación de un Analizador 
	descendente recursivo.  Cada método 
	implementa una sola regla de la 
	gramática.
	
	Use el metodo ._accept() para probar 
	y aceptar el token actualmente leido.  
	use el metodo ._expect() para 
	coincidir y descartar exactamente el 
	token siguiente en la entrada (o 
	levantar un SystemError si no coincide).
	
	El atributo .tok contiene el último
	token aceptado. El atributo .nexttok 
	contiene el siguiente token leido.
	'''
	def assignment(self):
		'''
		assignment : IDENT = expression ;
		'''
		if self._accept('IDENT'):
			name = self.tok.value
			self._expect('=')
			expr = self.expression()
			#self._expect(';')
			return WriteLocation(SimpleLocation(name), expr)
		else:
			raise SyntaxError('Esperando un identificador')
			
	def expression(self):
		'''
		expression : term { ('+'|'-') term }          # EBNF
		'''
		# You need to complete
		expr = self.term()
		while self._accept('+') or self._accept('-'):
			operator = self.tok.value
			right = self.term()
			expr = Binop(operator, expr, right)
		return expr
		
	def term(self):
		'''
		term : factor { ('*'|'/') factor }            # EBNF
		'''
		term = self.factor()
		while self._accept('*') or self._accept('/'):
			operator = self.tok.value
			right = self.factor()
			term = Binop(operator, term, right)
		return term
		
	def factor(self):
		'''
		factor : IDENT | NUMBER
				| ( expression )
		'''
		if self._accept('IDENT'):
			return ReadLocation(self.tok.value)
		elif self._accept('NUMBER'):
			return Number(self.tok.value)
		elif self._accept('('):
			expr = self.expression()
			self._expect(')')
			return expr
		else:
			raise SyntaxError('Esperando IDENT, NUMBER o (')
			
	# -----------------------------------------
	# Gunciones de Itilidad.  No cambie nada
	# 
	def _advance(self):
		'Advanced the tokenizer by one symbol'
		self.tok, self.nexttok = self.nexttok, next(self.tokens, None)
		
	def _accept(self,toktype):
		'Consume the next token if it matches an expected type'
		if self.nexttok and self.nexttok.type == toktype:
			self._advance()
			return True
		else:
			return False
			
	def _expect(self,toktype):
		'Consume and discard the next token or raise SyntaxError'
		if not self._accept(toktype):
			raise SyntaxError("Expected %s" % toktype)
			
	def start(self):
		'Entry point to parsing'
		self._advance()              # Load first lookahead token
		return self.assignment()
		
	def parse(self,tokens):
		'Entry point to parsing'
		self.tok = None         # Last symbol consumed
		self.nexttok = None     # Next symbol tokenized
		self.tokens = tokens
		return self.start()
		
# from rich import print

if __name__ == '__main__':
	text = "a = 1 + 2 * 3 / 4 - 5"
	lexer  = Tokenizer()
	parser = RecursiveDescentParser()
	ast    = parser.parse(lexer.tokenizer(text))
	
	print(ast)