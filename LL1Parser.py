#I need a Lexer analizer for any grammar:


    

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
            visited = set()  # Para evitar bucles infinitos en la recursión
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
                            break  # Si no contiene epsilon, no se puede agregar más
                        else:
                            first.remove('epsilon')  # Eliminar epsilon de los primeros
                else:
                    first.append('epsilon')  # Agregar epsilon solo si todos los símbolos producen epsilon
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
        input_string += '$'
        stack = ['$', self.grammar.keys()[0]]
        while stack:
            top = stack.pop()
            if top == input_string[0]:
                input_string = input_string[1:]
            elif self.terminal(top):
                return False
            elif top in self.grammar:
                if input_string[0] not in self.table[top]:
                    return False
                production = self.table[top][input_string[0]]
                if production[0] != 'epsilon':
                    stack += production[::-1]
        return True
    
    def print_first(self):
        for non_terminal in self.first:
            print ('First(', non_terminal, ') = {', ', '.join(self.first[non_terminal]), '}')

    def print_follow(self):
        for non_terminal in self.follow:
            print ('Follow(', non_terminal, ') = {', ', '.join(self.follow[non_terminal]), '}')

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
        self.print_table()

if __name__ == '__main__':
    grammar = {
        # Gramatica de prueba 1
        "S": [["A", "k", "O"]],
        "A": [["a", "A''"]],
        "A''": [["B", "A'"], ["C", "A'"]],
        "C": [["c"]],
        "B": [["b", "B", "C"], ["r"]],
        "A'": [["d", "A'"], ["epsilon"]]
        # Gramatica de prueba 2
        # "E": [["T", "E'"]],
        # "E'": [["+", "T", "E'"], ["-", "T", "E'"], ["epsilon"]],
        # "T": [["F", "T'"]],
        # "T'": [["*", "F", "T'"], ["/", "F", "T'"], ["epsilon"]],
        # "F": [["num"], ["(", "E", ")"]]
        # Gramatica de prueba 3
        # "S": [["u", "B", "D", "z"]],
        # "B": [["w", "B'"]],
        # "B'": [["v", "B'"], ["epsilon"]],
        # "D": [["E", "F"]],
        # "E": [["y"], ["epsilon"]],
        # "F": [["x"], ["epsilon"]]
    }

    # try:
    parser = LL1_Parser(grammar)
    parser.print_all()
    # except:
        # print('No es LL1')