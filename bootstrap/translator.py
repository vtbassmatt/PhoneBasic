import pprint
from lexer import tokenize
from parser import parse, PClear, PLabel, PLet, PPrint, PIf, PGoto, PExpr, PInput, PEnd


class TranslatorError(RuntimeError):
    pass


class Opcode(object):
    NOOP        = 0

    # screen stuff
    CLEAR       = 1
    PRINTNUM    = 2
    PRINTSTR    = 3

    # flow control
    GOTO        = 10

    # working with data
    LITERAL     = 20

    # make HALT really obvious
    HALT        = 255


def translate(ast):
    label_table = {}
    string_table = {}
    number_table = {}
    # by convention, put a magic number at the beginning
    # for this case, "PB01" in ASCII
    code = [ord("P"), ord("B"), ord("0"), ord("1")]

    for op in ast:
        if type(op) == PClear:
            code.append(Opcode.CLEAR)

        elif type(op) == PLabel:
            if op.id in label_table:
                raise TranslatorError("Label already exists", op.id)
            label_table[op.id] = len(code)

        elif type(op) == PGoto:
            if op.id in label_table:
                code.append(Opcode.LITERAL)         # push a location on the stack
                code.append(label_table[op.id])
                code.append(Opcode.GOTO)            # jump to it

        elif type(op) == PEnd:
            code.append(Opcode.HALT)

        else:
            code.append(Opcode.NOOP)

    return code


if __name__ == "__main__":
    program_text = """CLEAR
    top:
    LET a BE 25
    PRINT "Hello world", 27
    PRINT "Hello compiler"
    IF a < 2 THEN GOTO top
    PRINT "Passed the goto!"
    INPUT a, b
    END
    GOTO top
    """

    ast = parse(tokenize(program_text))
    print "AST:"
    pprint.pprint(ast)

    code = translate(ast)
    print "\nCode:"
    pprint.pprint(code)
