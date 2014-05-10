import pprint
from lexer import Token
import collections


class ParserError(RuntimeError):
    pass


PLabel  = collections.namedtuple('PLabel', ['id'])
PClear  = collections.namedtuple('PClear', [])
PLet    = collections.namedtuple('PLet', ['id', 'rhs'])
PPrint  = collections.namedtuple('PPrint', ['rhs'])
PInput  = collections.namedtuple('PInput', ['rhs'])
PIf     = collections.namedtuple('PIf', ['expr1', 'compop', 'expr2', 'stmt'])
PEnd    = collections.namedtuple('PEnd', [])
PGoto   = collections.namedtuple('PGoto', ['id'])
PExpr   = collections.namedtuple('PExpr', ['expr'])
PVar    = collections.namedtuple('PVar', ['id'])
PArith  = collections.namedtuple('PArith', ['op'])
PNumber = collections.namedtuple('PNumber', ['value'])


operator_table = {
    "*": { "precedence": 3, "left_associative": True },
    "/": { "precedence": 3, "left_associative": True },
    "+": { "precedence": 2, "left_associative": True },
    "-": { "precedence": 2, "left_associative": True },
}


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
            return PLabel(id.value)
        raise ParserError("error parsing line label", id)

    def m_let(self):
        (var, assign) = (self.next(), self.next())
        if var.typ == "ID" and assign.typ == "ASSIGN":
            self.next()
            return PLet(var.value, self.p_expr())
        raise ParserError("error parsing LET statement", self.token)

    def m_print(self):
        print_vals = []
        self.next()
        while True:
            if self.token.typ == "STRING":
                print_vals.append(self.token.value)
                self.next()
                continue
            elif self.token.typ == "COMMA":
                self.next()
                continue
            elif self.token.typ == "NEWLINE":
                break
            else:
                print_vals.append(self.p_expr())
                continue

        print_vals.append("\n")
        return PPrint(print_vals)

    def m_if(self):
        self.next()
        expr1 = self.p_expr()
        compop = self.token
        self.next()
        expr2 = self.p_expr()
        then = self.token
        if compop.typ == "COMPOP" and then.typ == "THEN":
            self.next()
            return PIf(expr1, compop.value, expr2, self.m_stmt())
        raise ParserError("error parsing IF statement", self.token)

    def m_goto(self):
        self.next()
        if self.token.typ == "ID":
            return PGoto(self.token.value)
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

        return PInput(input_vars)

    def m_clear(self):
        return PClear()

    def m_end(self):
        return PEnd()

    def p_expr(self):
        """Parse an expression, beginning with the current token.

        http://en.wikipedia.org/wiki/Shunting_yard_algorithm"""
        global operator_table

        allowed = ["NUMBER", "ID", "ARITHOP", "LPAREN", "RPAREN"]

        op_stack = []
        expr = []

        while self.token.typ in allowed:
            if self.token.typ == "NUMBER":
                expr.append(PNumber(value=self.token.value))

            elif self.token.typ == "ID":
                expr.append(PVar(id=self.token.value))

            elif self.token.typ == "ARITHOP":
                o1 = self.token.typ
                o1.la = operator_table[o1].left_associative
                o1.p = operator_table[o1].precedence
                o2 = op_stack[-1]
                while peek.typ == "ARITHOP":
                    o2.p = operator_table[o2].precedence
                    if (o1.la and o1.p == o2.p) or o1.p < o2.p:
                        op_stack.pop()
                        expr.append(PArith(op=o2.value))
                    else:
                        break
                    o2 = op_stack[-1]
                op_stack.append(o1)

            elif self.token.typ == "LPAREN":
                op_stack.push(self.token)

            elif self.token.typ == "RPAREN":
                # TODO: pop stuff and put on output queue until we hit a lparen
                # TODO: pop lparen
                # TODO: report an error if we empty the stack without finding lparen
                pass

            self.next()

        # TODO: while still operator tokens in stack
        # TODO: check if parenthesis: if so, mismatch
        # TODO: otherwise, pop onto queue

        return PExpr(expr)


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
        Token("NUMBER", "2", 7, 7),
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
