from sly import Lexer

class Lexer(Lexer):

    tokens = {
        #Palabras reservadas
        IF, ELSE, WHILE, FOR, IN, RETURN, BREAK, CONTINUE, FUNCTION, VAR, PRINT, READ,
        
        #Tipos de datos
        INT, FLOAT, STRING, BOOL,

        #Operadores
        ASSIGN, EQ, NEQ, LT, LE, GT, GE, AND, OR, NOT,

        #Idetificador
        ID,
    }

    literals = { '+', '-', '*', '/', '(', ')', '[', ']', '{', '}', ';', ',', ':' }

    #Definir tokens
    IF = r'if'
    ELSE = r'else'
    WHILE = r'while'
    FOR = r'for'
    IN = r'in'
    RETURN = r'return'
    BREAK = r'break'
    CONTINUE = r'continue'
    FUNCTION = r'function'
    VAR = r'var'
    PRINT = r'print'
    READ = r'read'
    
    FLOAT = r'\d*\.\d+(e-?\d+)?|\d+(e-?\d+)' # 1.2, 1.2e-3, 1e-3
    INT = r'\d+' # 123
    STRING = r'\".*\"'
    BOOL = r'true|false'

    EQ = r'=='
    NEQ = r'!='
    LE = r'<='
    GE = r'>='
    LT = r'<'
    GT = r'>'
    AND = r'&&'
    OR = r'\|\|'
    NOT = r'!'
    ASSIGN = r'='

    ID = r'[a-zA-Z_][a-zA-Z0-9_]*'

    #Ignorar espacios en blanco
    ignore = ' \t'

    #Ignorar comentarios
    ignore_comment = r'\/\/.*'

    #Ignorar saltos de linea
    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    #Manejo de errores
    def error(self, t):
        print('Caracter Ilegal %s' % t.value[0])
        self.index += 1
    

class LL1_Parser(object):
    
    def __init__(self, grammar):
        self.grammar = grammar
        self.first = {}
        self.follow = {}
        self.table = {}
        self.construct_first()
        self.construct_follow()
        self.construct_parse_table()

    def construct_first(self): 
        for non_terminal in self.grammar: 
            self.first[non_terminal] = self.calculate_first(non_terminal)
    
    def calculate_first(self, nt_symbol, visited=None):
        if visited is None:
            visited = set()  
        first = []
        if nt_symbol in visited:
            return first
        visited.add(nt_symbol)
        if nt_symbol in self.first:
            return self.first[nt_symbol]
        else:
            for production in self.grammar[nt_symbol]:
                for symbol in production:
                    if symbol == nt_symbol:
                        continue
                    elif symbol not in self.grammar:
                        first.append(symbol)
                        break
                    else:
                        symbol_first = self.calculate_first(symbol, visited)
                        first.extend(symbol_first)
                        if 'epsilon' not in symbol_first:
                            break  
                        else:
                            first.remove('epsilon')  
                else:
                    first.append('epsilon') 
        return first

    
    def construct_follow(self): 
        for non_terminal in self.grammar:
            self.follow[non_terminal] = self.calculate_follow(non_terminal)
    
    def calculate_follow(self, symbol):
        follow = []
        if symbol in self.follow:
            return self.follow[symbol]
        elif symbol == list(self.grammar.keys())[0]:
            follow.append('$')
        for non_terminal in self.grammar:
            for production in self.grammar[non_terminal]:
                if symbol in production:
                    index = production.index(symbol)
                    if index+1 == len(production):
                        if non_terminal != symbol:
                            followTerm = self.calculate_follow(non_terminal)
                            for terminal in followTerm:
                                if terminal not in follow:
                                    follow.append(terminal)
                    elif production[index + 1] not in self.grammar:
                            follow.append(production[index + 1])
                    else:
                        first = self.calculate_first(production[index + 1])
                        for terminal in first:
                            if terminal not in follow and terminal != 'epsilon':   
                                follow.append(terminal)
                        if 'epsilon' in first:
                            followTerm = self.calculate_follow(production[index + 1])
                            for terminal in followTerm:
                                if terminal not in follow:
                                    follow.append(terminal)
        return follow
    
    def is_nullable(self, symbol):
        return 'epsilon' in self.first[symbol]
    
    def construct_parse_table(self):
        for non_terminal in self.grammar:
            self.table[non_terminal] = self.construct_table(non_terminal)

    def construct_table(self, symbol):
        table = {}
        for production in self.grammar[symbol]:
            if production[0] == 'epsilon':
                for terminal in self.follow[symbol]:
                    table[terminal] = production
            elif production[0] not in self.grammar:
                table[production[0]] = production
            else:
                for terminal in self.calculate_first(production[0]):
                    table[terminal] = production
        return table
    
    def parse(self, input_string):
        print(self.grammar.keys())
        stack = ['$', list(self.grammar.keys())[0]]
        while stack:
            top = stack.pop()
            if len(input_string) == 0:
                if top == '$':
                    print('Aceptado')
            elif top == input_string[0].type:
                print(top, '->', input_string[0].value)
                input_string = input_string[1:]
            elif top in self.grammar:
                if input_string[0].type not in self.table[top]:
                    raise Exception('No es una gramática LL1')
                production = self.table[top][input_string[0].type]
                if production[0] != 'epsilon':
                    stack += production[::-1]
                print(top, '->', ' '.join(production))
    
    def print_first(self):
        for non_terminal in self.first:
            print ('First(', non_terminal, ') = {', ', '.join(self.first[non_terminal]), '}')

    def print_follow(self):
        for non_terminal in self.follow:
            print ('Follow(', non_terminal, ') = {', ', '.join(self.follow[non_terminal]), '}')

    def print_nullable(self):
        for non_terminal in self.first:
            print (non_terminal, 'Nullable: ', self.is_nullable(non_terminal))

    def print_table(self):
        for non_terminal in self.table:
            print ('M(', non_terminal, ') = {')
            for terminal in self.table[non_terminal]:
                print ('\t', terminal, ':', self.table[non_terminal][terminal])
            print ('}')
    
    def print_all(self):
        print ('First:')
        self.print_first()
        print ('Follow:')
        self.print_follow()
        # print ('Table:')
        print ('Nullable:')
        self.print_nullable()
        self.print_table()

if __name__ == '__main__':
    grammar = {
        # Gramatica de prueba 1
        # "S": [["A", "k", "O"]],
        # "A": [["a", "A''"]],
        # "A''": [["B", "A'"], ["C", "A'"]],
        # "C": [["c"]],
        # "B": [["b", "B", "C"], ["r"]],
        # "A'": [["d", "A'"], ["epsilon"]]
        # Gramatica de prueba 2
        "E": [["T", "E'"]],
        "E'": [["+", "T", "E'"], ["-", "T", "E'"], ["epsilon"]],
        "T": [["F", "T'"]],
        "T'": [["*", "F", "T'"], ["/", "F", "T'"], ["epsilon"]],
        "F": [["INT"], ["(", "E", ")"]]
        # Gramatica de prueba 3
        # "S": [["u", "B", "D", "z"]],
        # "B": [["w", "B'"]],
        # "B'": [["v", "B'"], ["epsilon"]],
        # "D": [["E", "F"]],
        # "E": [["y"], ["epsilon"]],
        # "F": [["x"], ["epsilon"]]
        # Gramatica de prueba 4
        #"S": [["A", "B", "C"]],
        #"A": [["a", "A"], ["epsilon"]],
        #"B": [["b", "B"], ["epsilon"]],
        #"C": [["c", "C"], ["epsilon"]]
        # Gramatica de prueba 5
        #"Program": [["Statement", "Program"], ["epsilon"]],
        #"Statement": [["VariableDeclaration"], ["Assignment"], ["Expression"]],
        #"VariableDeclaration": [["VAR", "ID", ":", "Type", ";"]],
        #"Assignment": [["ID", "=", "Expression", ";"]],
        #"Type": [["INT"], ["FLOAT"], ["STRING"], ["BOOL"]],
        #"Expression": [["Term", "Expression'"]],
        #"Expression'": [["+", "Term", "Expression'"], ["-", "Term", "Expression'"], ["epsilon"]],
        #"Term": [["Factor", "Term'"]],
        #"Term'": [["*", "Factor", "Term'"], ["/", "Factor", "Term'"], ["epsilon"]],
        #"Factor": [["ID"], ["INT"], ["FLOAT"], ["(", "Expression", ")"]]
        # Gramatica de prueba 6
        
    }

    data = '''1 * 2 - 3'''
    lexer = Lexer()
    tokens = []
    for tok in lexer.tokenize(data):
        tokens.append(tok)

    print(tokens)
    # data = ['number', '+', 'num', '*', 'num']
    parser = LL1_Parser(grammar)
    parser.print_all()
    parser.parse(tokens)

    # try:
    # parser.print_all()
    # except:
        # print('No es LL1')