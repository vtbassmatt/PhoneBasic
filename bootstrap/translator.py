import pprint
from lexer import tokenize
from parser import parse


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
    HALT        = 11

    # working with data
    LITERAL     = 20


def translate(ast):
    label_table = {}
    string_table = {}
    number_table = {}
    # by convention, put a magic number at the beginning
    # for this case, "PB01" in ASCII
    code = [ord("P"), ord("B"), ord("0"), ord("1")]

    for line in ast:
        if line[0] == 'clear':
            code.append(Opcode.CLEAR)

        elif line[0] == 'label':
            label = line[1]
            if label in label_table:
                raise TranslatorError("Label already exists", label)
            label_table[label] = len(code)

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
    """

    ast = parse(tokenize(program_text))
    print "AST:"
    pprint.pprint(ast)

    code = translate(ast)
    print "\nCode:"
    pprint.pprint(code)
