import pprint
from lexer import Token

class ParserError(RuntimeError):
    pass


class Parser(object):
    def __init__(self, tokens):
        self.token_iter = iter(tokens)
        self.token = None

    def next(self):
        return self.token_iter.next()

    def parse(self):
        ast = []
        while True:
            try:
                self.token = self.next()
            except StopIteration:
                break

            if self.token.typ == "NEWLINE":
                continue

            elif self.token.typ == "ID":    # should be a line label
                ast.append(self.m_label())
                continue

            elif self.token.typ == "LET":
                ast.append(self.m_let())
                continue

            elif self.token.typ == "PRINT":
                ast.append(self.m_print())
                continue

            else:
                raise ParserError("unexpected token", self.token)

        return ast

    def m_label(self):
        (colon, newline) = (self.next(), self.next())
        # make sure colon and newline matched
        if colon.typ == "COLON" and newline.typ == "NEWLINE":
            return ["label", self.token.value]
        raise ParserError("error parsing line label", self.token)

    def m_let(self):
        (var, assign) = (self.next(), self.next())
        if var.typ == "ID" and assign.typ == "ASSIGN":
            self.token = self.next()
            return ["let", var.value, self.p_expr(["NEWLINE"])]
        raise ParserError("error parsing LET statement", self.token)

    def m_print(self):
        print_vals = []
        while True:
            self.token = self.next()
            if self.token.typ == "STRING":
                print_vals.append(self.token.value)
                continue
            elif self.token.typ == "COMMA":
                continue
            elif self.token.typ == "NEWLINE":
                break
            else:
                print_vals.append(self.p_expr())
                #if next.typ == "NEWLINE":
                #    break
                continue

        print_vals.append("\n")
        return ["print", print_vals]

    def p_expr(self, terminators = None):
        if terminators == None:
            terminators = ["NEWLINE", "COMMA"]
        allowed = ["NUMBER", "ID", "ARITHOP"]

        # TODO: read more than just the next token
        #self.token = self.next()
        return ["expr", self.token.value]


def parse(tokens):
    return Parser(tokens).parse()


if __name__ == "__main__":
    ast = parse([
        Token("ID", "top", 1, 0),
        Token("COLON", ":", 1, 3),
        Token("NEWLINE", "\n", 1, 4),
        Token("LET", "LET", 2, 0),
        Token("ID", "a", 2, 4),
        Token("ASSIGN", "BE", 2, 6),
        Token("NUMBER", "25", 2, 9),
        Token("NEWLINE", "\n", 2, 11),
        Token("PRINT", "PRINT", 3, 0),
        Token("STRING", "Hello world", 3, 6),
        Token("COMMA", ",", 3, 19),
        Token("NUMBER", "27", 3, 21),
        Token("NEWLINE", "\n", 3, 23),
        Token("PRINT", "PRINT", 4, 0),
        Token("STRING", "Hello compiler", 4, 6),
        Token("NEWLINE", "\n", 4, 22),
    ])

    pprint.pprint(ast)
