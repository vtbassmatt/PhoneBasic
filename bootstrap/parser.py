import pprint
from lexer import Token

class ParserError(RuntimeError):
    pass


class Parser(object):
    def __init__(self, tokens):
        self.tokens = tokens

    def parse(self):
        ast = []
        token_iter = iter(self.tokens)
        while True:
            try:
                token = token_iter.next()
            except StopIteration:
                break

            if token.typ == "NEWLINE":
                continue

            elif token.typ == "ID":    # should be a line label
                ast.append(self.m_label(token, token_iter))
                continue

            elif token.typ == "LET":
                ast.append(self.m_let(token, token_iter))
                continue

            elif token.typ == "PRINT":
                ast.append(self.m_print(token, token_iter))
                continue

            else:
                raise ParserError("unexpected token at line " + token.line)

        return ast

    def m_label(self, label_token, token_iter):
        (colon, newline) = (token_iter.next(), token_iter.next())
        # make sure colon and newline matched
        if colon.typ == "COLON" and newline.typ == "NEWLINE":
            return ["label", label_token.value]
        raise ParserError("error parsing line label")

    def m_let(self, let_token, token_iter):
        (var, assign, expr) = (token_iter.next(), token_iter.next(), token_iter.next())
        # TODO: expression parser
        if var.typ == "ID" and assign.typ == "ASSIGN":
            return ["let", var.value, expr.value]
        raise ParserError("error parsing LET statement")

    def m_print(self, print_token, token_iter):
        output = token_iter.next()
        # TODO: string | expression list (requires lookahead)
        if output.typ == "STRING":
            return ["print", [output.value, "\n"]]
        raise ParserError("error parsing PRINT statement")


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
        Token("NEWLINE", "\n", 3, 19),
        Token("PRINT", "PRINT", 4, 0),
        Token("STRING", "Hello compiler", 4, 6),
        Token("NEWLINE", "\n", 4, 22),
    ])

    pprint.pprint(ast)
