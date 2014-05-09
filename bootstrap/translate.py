import pprint
from lexer import tokenize
from parser import parse

def translate(ast):
    # TODO: write this
    pass

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
