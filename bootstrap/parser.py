import pprint
import sys
from lexer import Token
import collections


class ParserError(RuntimeError):
    pass


PLabel   = collections.namedtuple('PLabel', ['id'])
PClear   = collections.namedtuple('PClear', [])
PLet     = collections.namedtuple('PLet', ['id', 'rhs'])
PPrint   = collections.namedtuple('PPrint', ['rhs'])
PInput   = collections.namedtuple('PInput', ['rhs'])
PIf      = collections.namedtuple('PIf', ['expr1', 'compop', 'expr2', 'stmt'])
PEnd     = collections.namedtuple('PEnd', [])
PGoto    = collections.namedtuple('PGoto', ['id'])
PString  = collections.namedtuple('PString', ['value'])
PExpr    = collections.namedtuple('PExpr', ['expr'])
PVar     = collections.namedtuple('PVar', ['id'])
PArith   = collections.namedtuple('PArith', ['op'])
PNumber  = collections.namedtuple('PNumber', ['value'])
PCall    = collections.namedtuple('PCall', ['label'])
PCompute = collections.namedtuple('PCompute', ['label', 'id', 'args'])
PReturn  = collections.namedtuple('PReturn', ['expr'])
PAccept  = collections.namedtuple('PAccept', ['rhs'])


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

        elif self.token.typ == "CALL":
            return self.m_call()

        elif self.token.typ == "COMPUTE":
            return self.m_compute()

        elif self.token.typ == "RETURN":
            return self.m_return()

        elif self.token.typ == "ACCEPT":
            return self.m_accept()

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
            return PLet(var.value, self.p_expr_or_string())
        raise ParserError("error parsing LET statement", self.token)

    def m_return(self):
        self.next()
        if self.token.typ == "NEWLINE":
            return PReturn(expr=None)
        else:
            return PReturn(expr=self.p_expr())

    def m_call(self):
        label = self.next()
        if label.typ == "ID":
            return PCall(label=label.value)
        else:
            raise ParserError("error parsing CALL, expected a label", self.token)

    def m_compute(self):
        (var, az, label) = (self.next(), self.next(), self.next())
        if var.typ == "ID" and az.typ == "AS" and label.typ == "ID":
            self.next()
            return PCompute(label=label.value, id=var.value, args=self.p_arglist())
        else:
            raise ParserError("error parsing COMPUTE")

    def m_accept(self):
        accept_vals = []
        self.next()
        while True:
            if self.token.typ == "ID":
                accept_vals.append(PVar(self.token.value))
                self.next()
                continue
            elif self.token.typ == "COMMA":
                self.next()
                continue
            elif self.token.typ == "NEWLINE":
                break
            else:
                raise ParserError("unexpected token", self.token)

        return PAccept(accept_vals)

    def m_print(self):
        print_vals = []
        self.next()
        while True:
            if self.token.typ == "COMMA":
                self.next()
                continue
            elif self.token.typ == "NEWLINE":
                break
            else:
                print_vals.append(self.p_expr_or_string())
                continue

        print_vals.append(PString(value="\n"))
        return PPrint(print_vals)

    def m_if(self):
        self.next()
        expr1 = self.p_expr_or_string()
        compop = self.token
        self.next()
        expr2 = self.p_expr_or_string()
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
                input_vars.append(PVar(self.token.value))
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

    def p_arglist(self):
        args = []
        while self.token.typ != "NEWLINE":
            if self.token.typ == "COMMA":
                break

            else:
                args.append(self.p_expr())

            self.next()

        return args

    def p_expr_or_string(self):
        if self.token.typ == "STRING":
            string_token = self.token
            self.next()
            return PString(string_token.value)
        else:
            return self.p_expr()

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
                o1 = self.token
                o1la = operator_table[o1.value]["left_associative"]
                o1p = operator_table[o1.value]["precedence"]
                try:
                    o2 = op_stack[-1]
                    while o2.typ == "ARITHOP":
                        o2p = operator_table[o2.value]["precedence"]
                        if (o1la and o1p == o2p) or o1p < o2p:
                            op_stack.pop()
                            expr.append(PArith(op=o2.value))
                        else:
                            break
                        o2 = op_stack[-1]
                except IndexError:
                    # op_stack is empty
                    pass
                op_stack.append(o1)

            elif self.token.typ == "LPAREN":
                op_stack.append(self.token)

            elif self.token.typ == "RPAREN":
                try:
                    peek = op_stack[-1]
                    while peek.typ != "LPAREN":
                        op_stack.pop()
                        expr.append(PArith(op=peek.value))
                        peek = op_stack[-1]
                except IndexError:
                    pass

                # now the stack is either empty or has LPAREN at the top
                if len(op_stack) > 0:
                    op_stack.pop()
                else:
                    raise ParserError("mismatched parentheses, expected '('", self.token)

                pass

            self.next()

        while len(op_stack) > 0:
            remaining_op = op_stack.pop()
            if remaining_op.typ != "LPAREN":
                expr.append(PArith(op=remaining_op.value))
            else:
                raise ParserError("mismatched parentheses, expected ')'", remaining_op)

        return PExpr(expr)


def parse(tokens):
    return Parser(tokens).parse()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        print "opening file", sys.argv[1]
        from lexer import tokenize
        with open(sys.argv[1], 'r') as f:
            statements = f.read()
            ast = parse(tokenize(statements))
    else:
        print "using baked-in file"
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

            Token("LET", "LET", 10, 0),
            Token("ID", "c", 10, 4),
            Token("ASSIGN", "BE", 10, 6),
            Token("ID", "a", 10, 9),
            Token("ARITHOP", "+", 10, 10),
            Token("LPAREN", "(", 10, 11),
            Token("ID", "b", 10, 12),
            Token("ARITHOP", "-", 10, 13),
            Token("NUMBER", "1", 10, 14),
            Token("RPAREN", ")", 10, 15),
            Token("NEWLINE", "\n", 10, 16),

            Token("END", "END", 20, 0),
        ])

    pprint.pprint(ast)
