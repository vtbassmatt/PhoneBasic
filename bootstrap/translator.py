import pprint
from lexer import tokenize
from parser import parse, PClear, PLabel, PLet, PPrint, PIf, PGoto, PInput, PEnd
from parser import PExpr, PVar, PNumber, PArith


class TranslatorError(RuntimeError):
    pass


class Opcode(object):
    """Opcodes for this virtual machine.

    It is a stack-based machine with only one register, the name register.

    Numbers and strings are stored in tables separate from main memory,
    they're accessed by certain opcodes using the name register."""

    NOOP        = 0

    # screen stuff
    CLEAR       = 1
    PRINTNUM    = 2     # nummem[@(namereg)] sent to output
    PRINTLIT    = 3     # [a] => [], number 'a' sent to output
    PRINTSTR    = 4     # strmem[@(namereg)] sent to output

    # flow control
    GOTO        = 10

    # working with data
    LITERAL     = 20    # [] => [@(IP)++]
    NAME        = 21    # [a] => [], next 'a' bytes read into name register, IP+=a
    STORENUM    = 22    # [a] => [], nummem[@(namereg)] = a
    RETRVNUM    = 23    # [] => [nummem[@(namereg)]]
    DELETENUM   = 24    # nummem[@(namereg)] unset
    #TODO: store and delete strings

    # math
    ADD         = 40
    SUBTRACT    = 41
    MULTIPLY    = 42
    DIVIDE      = 43

    # make HALT really obvious
    HALT        = 255


def translate(ast):
    label_table = {}
    string_table = {}
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
            else:
                raise NotImplementedError("back-references are not ready", op)

        elif type(op) == PLet:
            codegen_let(op, code)

        elif type(op) == PEnd:
            code.append(Opcode.HALT)

        else:
            code.append(Opcode.NOOP)

    return code


def codegen_let(op, code):
    codegen_name(op.id, code)

    if type(op.rhs) == PExpr:
        codegen_expr(op.rhs, code)
    else:
        raise NotImplementedError("LET statements for strings are not ready")

def codegen_name(name, code):
    code.append(Opcode.LITERAL)
    code.append(len(name))
    code.append(Opcode.NAME)
    for letter in name:
        code.append(ord(letter))

def codegen_expr(expr_token, code):
    # expressions expected in reverse polish notation
    if type(expr_token) != PExpr:
        raise TranslatorError("expected an expression to parse", expr_token)
    for op in expr_token.expr:
        if type(op) == PNumber:
            # TODO: deal with numbers > 255 and actually deal with floats
            code.append(Opcode.LITERAL)
            if "." in op.value:
                code.append(float(op.value))
            else:
                code.append(int(op.value))

        elif type(op) == PArith:
            if op.op == "+":
                code.append(Opcode.ADD)
            elif op.op == "-":
                code.append(Opcode.SUBTRACT)
            elif op.op == "*":
                code.append(Opcode.MULTIPLY)
            elif op.op == "/":
                code.append(Opcode.DIVIDE)
            else:
                raise TranslatorError("unknown arithmetic operator", op)

        elif type(op) == PVar:
            codegen_read_var(op, code)

        else:
            # the given expression contained tokens we don't understand
            raise TranslatorError("unknown token type in expression", op)

def codegen_read_var(op, code):
    if type(op) != PVar:
        raise TranslatorError("expected a variable", op)
    codegen_name(op.id, code)
    code.append(Opcode.RETRVNUM)


# quick and dirty disassembler
def disassemble(code):
    def addr(a):
        return "{:#04x}".format(a)

    i = 4
    print "Metadata: " + str([chr(a) for a in code[0:4]])
    while i < len(code):
        if code[i] == Opcode.NOOP:
            print addr(i) + " NOOP"

        elif code[i] == Opcode.CLEAR:
            print addr(i) + " CLEAR"

        elif code[i] == Opcode.PRINTNUM:
            print addr(i) + " PRINTNUM"

        elif code[i] == Opcode.PRINTLIT:
            print addr(i) + " PRINTLIT"

        elif code[i] == Opcode.PRINTSTR:
            print addr(i) + " PRINTSTR"

        elif code[i] == Opcode.GOTO:
            print addr(i) + " GOTO"

        elif code[i] == Opcode.LITERAL:
            print addr(i) + " LITERAL " + str(code[i+1])
            i += 1
            print addr(i) + "         ^"

#         elif code[i] == Opcode.NAME:
#             name = ""
#             i += 1
#             for letter in code[i:i+last_literal]:
#                 name += chr(letter)
#             print addr(i-1) + " NAME '" + name + "'"
#             i += last_literal

        elif code[i] == Opcode.STORENUM:
            print addr(i) + " STORENUM"

        elif code[i] == Opcode.RETRVNUM:
            print addr(i) + " RETRVNUM"

        elif code[i] == Opcode.DELETENUM:
            print addr(i) + " DELETENUM"

        elif code[i] == Opcode.ADD:
            print addr(i) + " ADD"

        elif code[i] == Opcode.SUBTRACT:
            print addr(i) + " SUBTRACT"

        elif code[i] == Opcode.MULTIPLY:
            print addr(i) + " MULTIPLY"

        elif code[i] == Opcode.DIVIDE:
            print addr(i) + " DIVIDE"

        elif code[i] == Opcode.HALT:
            print addr(i) + " HALT"

        else:
            print addr(i) + " ?? " + str(code[i])

        i += 1


if __name__ == "__main__":
    program_text = """CLEAR
    top:
    LET a BE 25 + b
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

    print "\nDisassembly:"
    disassemble(code)
