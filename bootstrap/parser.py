import pprint
from lexer import Token

class ParserError(RuntimeError):
    pass


class Parser(object):
    def __init__(self, tokens):
        self.token_iter = iter(tokens)
        self.token = None

    def next(self):
        self.token = self.token_iter.next()
        return self.token

    def parse(self):
        ast = []
        while True:
            try:
                self.next()
            except StopIteration:
                break

            if self.token.typ == "NEWLINE":
                continue

            elif self.token.typ == "ID":    # should be a line label
                ast.append(self.m_label())
                continue

            else:
                ast.append(self.m_stmt())

        return ast

    def m_stmt(self):
        if self.token.typ == "LET":
            return self.m_let()

        elif self.token.typ == "PRINT":
            return self.m_print()

        elif self.token.typ == "IF":
            return self.m_if()

        elif self.token.typ == "GOTO":
            return self.m_goto()

        elif self.token.typ == "INPUT":
            return self.m_input()

        elif self.token.typ == "CLEAR":
            return self.m_clear()

        elif self.token.typ == "END":
            return self.m_end()

        else:
            raise ParserError("unexpected token", self.token)

    def m_label(self):
        id = self.token
        (colon, newline) = (self.next(), self.next())
        # make sure colon and newline matched
        if colon.typ == "COLON" and newline.typ == "NEWLINE":
            return ["label", id.value]
        raise ParserError("error parsing line label", id)

    def m_let(self):
        (var, assign) = (self.next(), self.next())
        if var.typ == "ID" and assign.typ == "ASSIGN":
            self.next()
            return ["let", var.value, self.p_expr()]
        raise ParserError("error parsing LET statement", self.token)

    def m_print(self):
        print_vals = []
        while True:
            self.next()
            if self.token.typ == "STRING":
                print_vals.append(self.token.value)
                continue
            elif self.token.typ == "COMMA":
                continue
            elif self.token.typ == "NEWLINE":
                break
            else:
                print_vals.append(self.p_expr())
                continue

        print_vals.append("\n")
        return ["print", print_vals]

    def m_if(self):
        self.next()
        expr1 = self.p_expr()
        compop = self.next()
        self.next()
        expr2 = self.p_expr()
        then = self.next()
        if compop.typ == "COMPOP" and then.typ == "THEN":
            self.next()
            return ["if", expr1, compop.value, expr2, self.m_stmt()]
        raise ParserError("error parsing IF statement", self.token)

    def m_goto(self):
        self.next()
        if self.token.typ == "ID":
            return ["goto", self.token.value]
        raise ParserError("error parsing GOTO statement", self.token)

    def m_input(self):
        input_vars = []
        while True:
            self.next()
            if self.token.typ == "ID":
                input_vars.append(self.token.value)
                continue
            elif self.token.typ == "COMMA":
                continue
            elif self.token.typ == "NEWLINE":
                break
            else:
                raise ParserError("error parsing INPUT statement", self.token)

        return ["input", input_vars]

    def m_clear(self):
        return ["clear"]

    def m_end(self):
        return ["end"]

    def p_expr(self):
        """Parse an expression."""
        allowed = ["NUMBER", "ID", "ARITHOP"]

        # TODO: read more than just the next token
        return ["expr", self.token.value]


def parse(tokens):
    return Parser(tokens).parse()


if __name__ == "__main__":
    ast = parse([
        Token("CLEAR", "CLEAR", 1, 0),

        Token("ID", "top", 3, 0),
        Token("COLON", ":", 3, 3),
        Token("NEWLINE", "\n", 3, 4),

        Token("LET", "LET", 4, 0),
        Token("ID", "a", 4, 4),
        Token("ASSIGN", "BE", 4, 6),
        Token("NUMBER", "25", 4, 9),
        Token("NEWLINE", "\n", 4, 11),

        Token("PRINT", "PRINT", 5, 0),
        Token("STRING", "Hello world", 5, 6),
        Token("COMMA", ",", 5, 19),
        Token("NUMBER", "27", 5, 21),
        Token("NEWLINE", "\n", 5, 23),

        Token("PRINT", "PRINT", 6, 0),
        Token("STRING", "Hello compiler", 6, 6),
        Token("NEWLINE", "\n", 6, 22),

        Token("IF", "IF", 7, 0),
        Token("ID", "a", 7, 3),
        Token("COMPOP", "<", 7, 5),
        Token("NUMBER", "25", 7, 7),
        Token("THEN", "THEN", 7, 10),
        Token("PRINT", "PRINT", 7, 15),
        Token("STRING", "Less than 2", 7, 22),
        Token("NEWLINE", "\n", 7, 33),

        Token("GOTO", "GOTO", 8, 0),
        Token("ID", "top", 8, 5),
        Token("NEWLINE", "\n", 8, 8),

        Token("INPUT", "INPUT", 9, 0),
        Token("ID", "a", 9, 7),
        Token("COMMA", ",", 9, 8),
        Token("ID", "b", 9, 10),
        Token("NEWLINE", "\n", 9, 11),

        Token("END", "END", 20, 0),
    ])

    pprint.pprint(ast)
