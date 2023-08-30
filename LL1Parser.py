

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

    def construct_follow(self):
        for non_terminal in self.grammar:
            self.follow[non_terminal] = self.calculate_follow(non_terminal)
    
    def calculate_first(self, symbol):
        first = []
        if symbol in self.first:
            return self.first[symbol]
        else:
            for production in self.grammar[symbol]:
                if production[0] == 'epsilon':
                    continue
                elif production[0] not in self.grammar:
                    first.append(production[0])
                else:
                    first += self.calculate_first(production[0])
        return first
    
    def calculate_follow(self, symbol):
        follow = []
        if symbol in self.follow:
            return self.follow[symbol]
        elif symbol == 'E':
            follow.append('$')
        for non_terminal in self.grammar:
            for production in self.grammar[non_terminal]:
                if symbol in production:
                    index = production.index(symbol)
                    if index+1 == len(production) or index == 0:
                        if non_terminal != symbol:
                            follow += self.calculate_follow(non_terminal)
                    elif production[index + 1] not in self.grammar:
                            follow.append(production[index + 1])
                    else:
                        first = self.calculate_first(production[index + 1])
                        for terminal in first:
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
        print('Tabla de sintaxis', end='')
        for non_terminal in self.table:
            print (f'\n {non_terminal}', end='')
            for terminal in self.table[non_terminal]:
                print (f'\t{terminal} : {self.table[non_terminal][terminal]}', end='|')
    
    def print_all(self):
        print ('First:')
        self.print_first()
        print ('Follow:')
        self.print_follow()
        # print ('Table:')
        self.print_table()

if __name__ == '__main__':
    grammar = {
        "E": [["T", "E'"]],
        "E'": [["+", "T", "E'"], ["-", "T", "E'"], ["epsilon"]],
        "T": [["F", "T'"]],
        "T'": [["*", "F", "T'"], ["/", "F", "T'"], ["epsilon"]],
        "F": [["num"], ["(", "E", ")"]]
    }
    parser = LL1_Parser(grammar)
    parser.print_all()