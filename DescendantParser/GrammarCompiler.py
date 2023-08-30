'''
analizador descendente recursivo para la gramática:
    prog ::= 'BEGIN' stmts 'END'

    stmts ::= stmt*

    stmt ::= printstmt
    			| ifstmt
    			| assignstmt

    printstmt ::= 'PRINT' exprlist ';'

    ifstmt ::= 'IF' '(' expr ')' 'THEN' expr ';'

    assignstmt ::= IDENT '=' expr ';'

    expr ::= term '+' expr
    			| term '-' expr
    			| term

    term ::= factor '*' term
    			| factor '/' term
    			| factor

    factor ::= literal
    			| IDENT
    			| '(' expr ')'

    literal ::= ICONST
    			| RCONST
    			| SCONST

    exprlist ::= expr (',' expr)*

IMPORTANTE: No existe una sentencia para IDENT, por lo que se declara como sigue: IDENT ::= [a-zA-Z][0-9]
Así mismo, no existe definición para ICONST, RCONST, SCONST, por lo que se declaran como sigue:
    ICONST ::= [0-9]+(\.[0-9]+)?(E[-+]?[0-9]+)?
    RCONST ::= '<=', '>=', '<>','<', '>'
    SCONST ::= '"'.'"'
'''

#Importaciones
import re
from dataclasses import dataclass
from model import *

#Analizador léxico

#Clase Token
@dataclass
class Token(object):
  type: str
  value: float or str
  lineno: int = 1

#Clase Tokenizer
class Tokenizer(object):
  tokens = [
    #Palabras reservadas
    (r'BEGIN|begin', lambda s,tok: Token('BEGIN', tok)),
    (r'END|end', lambda s,tok: Token('END', tok)),
    (r'PRINT|print', lambda s,tok: Token('PRINT', tok)),
    (r'IF|if', lambda s,tok: Token('IF', tok)),
    (r'THEN|then', lambda s,tok: Token('THEN', tok)),

    #Constantes
    (r'\d+(\.\d+)?(E[-+]?\d+)?', lambda s,tok: Token('ICONST', tok)),
    (r'<=|>=|<>|<|>', lambda s,tok: Token('RCONST', tok)),
    (r'".*\s?"', lambda s,tok: Token('SCONST', tok)),
    (r';', lambda s,tok: Token(';', tok)),
    (r',', lambda s,tok: Token(',', tok)),
    (r'\(', lambda s,tok: Token('(', tok)),
    (r'\)', lambda s,tok: Token(')', tok)),
    (r'//.*\s?', None),
    
    #Operadores
    (r'\+', lambda s,tok: Token('+', tok)),
    (r'-', lambda s,tok: Token('-', tok)),
    (r'\*', lambda s,tok: Token('*', tok)),
    (r'/', lambda s,tok: Token('/', tok)),
    (r'=', lambda s,tok: Token('=', tok)),

    #Identificador
    (r'[a-z][a-zA-Z]*[0-9]*', lambda s,tok: Token('IDENT', tok)),
   
    (r'\s', None),
    (r'.' , lambda s,tok: print('ERROR: caracter ilegal', tok))
  ]

  def tokenizer(self, text):
    scanner = re.Scanner(self.tokens)
    results, remainder = scanner.scan(text)
    return iter(results)

#Analizador sintáctico

#Parser descendente recursivo

#Clase Parser
@dataclass
class DescendantParser(object):
  #Métodos de la gramática
  def prog(self):
    #prog ::= 'BEGIN' stmts 'END'
    self._accept('BEGIN')
    stmts = self.stmts()
    self._accept('END')
    return stmts
  
  def stmts(self):
    #stmts ::= stmt*
    stmts = []
    while self.next_tok.type != 'END':
      stmts.append(self.stmt())
    return stmts
  
  def stmt(self):
    #stmt ::= printstmt| ifstmt| assignstmt
    if self.next_tok.type == 'PRINT':
      return self.printstmt()
    elif self.next_tok.type == 'IF':
      return self.ifstmt()
    elif self.next_tok.type == 'IDENT':
      return self.assignstmt()
    else:
      raise SyntaxError('Se esperaba una sentencia {}'.format(self.next_tok))

  def printstmt(self):
    #printstmt ::= 'PRINT' exprlist ';'
    self._accept('PRINT')
    exprlist = self.exprlist()
    self._expect(';')
    return exprlist
  
  def exprlist(self):
    #exprlist ::= expr (',' expr)*
    exprlist = [self.expr()]
    while self._accept(','):
      exprlist.append(self.expr())
    return exprlist
  
  def ifstmt(self):
    #ifstmt ::= 'IF' '(' expr ')' 'THEN' expr ';'
    self._accept('IF')
    self._accept('(')
    condition = self.expr()
    self._expect(')')
    self._expect('THEN')
    if (self.next_tok.type == 'PRINT' or self.next_tok.type == 'IF'):
      then = self.stmt()
    else:
      then = self.expr()
      self._expect(';')
    return condition, then

  def assignstmt(self):
    # assignstmt ::= IDENT '=' expr ';'
    if self._accept('IDENT'):
      name = self.tok.value
      self._expect('=')
      expr = self.expr()
      self._expect(';')
      return WriteLocation(SimpleLocation(name), expr)
    else:
      raise SyntaxError('Se esperaba un identificador')
      
  def expr(self):
    #expr ::= term '+' expr| term '-' expr| term
    expr = self.term()
    while self._accept('+') or self._accept('-'):
      operator = self.tok.value
      right = self.expr()
      expr = Binop(operator, expr, right)
    return expr
      
  def term(self):
    #term ::= factor '*' term| factor '/' term| factor
    term = self.factor()
    while self._accept('*') or self._accept('/'):
      operator = self.tok.value
      right = self.term()
      term = Binop(operator, term, right)
    return term
  
  def factor(self):
    #factor ::= literal| IDENT| '(' expr ')'
    if self._accept('ICONST') or self._accept('RCONST') or self._accept('SCONST'):
      return self.tok.value
    elif self._accept('IDENT'):
      name = self.tok.value
      return ReadLocation(name)
    elif self._accept('('):
      expr = self.expr()
      self._expect(')')
      return expr
    else:
        raise SyntaxError('Se esperaba un factor {}'.format(self.next_tok))
  
  #Métodos de la clase Parser

  def advance(self):
    self.tok, self.next_tok = self.next_tok, next(self.tokens, None)

  def _accept(self, token_type):
    if self.next_tok and self.next_tok.type == token_type:
      self.advance()
      return True
    else:
      return False
      
  def _expect(self, token_type):
    if not self._accept(token_type):
      raise SyntaxError('Se esperaba un token del tipo {} se obtuvo {}'.format(token_type, self.next_tok))
    
  def parse(self, tokens):
    self.tokens = tokens
    self.tok = None
    self.next_tok = None
    self.advance()
    return self.prog()
      
if __name__ == '__main__':
  text = './customTest.txt'
  with open(text, 'r') as f:
    text = f.read()
  lexer = Tokenizer()
  parser = DescendantParser()
  # tokens = lexer.tokenizer(text)
  # for token in tokens:
  #   print(token)
  # print('\n')
  ast = parser.parse(lexer.tokenizer(text))
  print(ast)
