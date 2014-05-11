import pprint
import collections
from lexer import tokenize
from parser import parse, PClear, PLabel, PLet, PPrint, PIf, PGoto, PInput, PEnd
from parser import PExpr, PVar, PNumber, PArith, PString


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
    PRINTNUMLIT = 3     # [a] => [], number 'a' sent to output
    PRINTSTR    = 4     # strmem[@(namereg)] sent to output
    PRINTSTRLIT = 5     # [a] => [], strtab[a] sent to output

    # flow control
    GOTO        = 10

    # working with data
    LITERAL     = 20    # [] => [@(IP)++]
    NAME        = 21    # a = @(IP+1), next 'a' bytes read into name register, IP=IP+a+1
    STORENUM    = 22    # [a] => [], nummem[@(namereg)] = a
    RETRVNUM    = 23    # [] => [nummem[@(namereg)]]
    DELETENUM   = 24    # nummem[@(namereg)] unset
    STORESTR    = 25    # [a] => [], strmem[@(namereg)] = strtab[a]

    # math
    ADD         = 40
    SUBTRACT    = 41
    MULTIPLY    = 42
    DIVIDE      = 43

    # make HALT really obvious
    HALT        = 255


TContext = collections.namedtuple('TContext',
    ['label_table', 'string_table', 'code'])


def translate(ast):
    ctx = TContext(
        label_table = {},
        string_table = [],
        # by convention, put a magic number at the beginning
        # for this case, "PB01" in ASCII
        code = [ord("P"), ord("B"), ord("0"), ord("1")]
    )

    for op in ast:
        if type(op) == PClear:
            ctx.code.append(Opcode.CLEAR)

        elif type(op) == PLabel:
            if op.id in ctx.label_table:
                raise TranslatorError("Label already exists", op.id)
            ctx.label_table[op.id] = len(ctx.code)

        elif type(op) == PGoto:
            if op.id in ctx.label_table:
                ctx.code.append(Opcode.LITERAL)         # push a location on the stack
                ctx.code.append(ctx.label_table[op.id])
                ctx.code.append(Opcode.GOTO)            # jump to it
            else:
                raise NotImplementedError("back-references are not ready", op)

        elif type(op) == PLet:
            codegen_let(op, ctx)

        elif type(op) == PPrint:
            codegen_print(op, ctx)

        elif type(op) == PEnd:
            ctx.code.append(Opcode.HALT)

        else:
            ctx.code.append(Opcode.NOOP)

    return (ctx.code, ctx.string_table)


def codegen_print(op, ctx):
    if type(op) != PPrint:
        raise TranslatorError("expected a print statement", op)
    for printable in op.rhs:
        if type(printable) == PString:
            codegen_str(printable, ctx)
            ctx.code.append(Opcode.PRINTSTRLIT)
        elif type(printable) == PExpr:
            # TODO: handle expressions
            pass

def codegen_let(op, ctx):
    name = op.id

    if type(op.rhs) == PExpr:
        codegen_expr(op.rhs, ctx)
        codegen_name(name, ctx)
        ctx.code.append(Opcode.STORENUM)
    elif type(op.rhs) == PString:
        codegen_str(op.rhs, ctx)
        codegen_name(name, ctx)
        ctx.code.append(Opcode.STORESTR)
    else:
        raise TranslatorError("don't know how to transform the RHS", op)

def codegen_name(name, ctx):
    ctx.code.append(Opcode.NAME)
    ctx.code.append(len(name))
    for letter in name:
        ctx.code.append(ord(letter))

def codegen_expr(expr_token, ctx):
    # expressions expected in reverse polish notation
    if type(expr_token) != PExpr:
        raise TranslatorError("expected an expression to parse", expr_token)
    for op in expr_token.expr:
        if type(op) == PNumber:
            # TODO: deal with numbers > 255 and actually deal with floats
            ctx.code.append(Opcode.LITERAL)
            if "." in op.value:
                ctx.code.append(float(op.value))
            else:
                ctx.code.append(int(op.value))

        elif type(op) == PArith:
            if op.op == "+":
                ctx.code.append(Opcode.ADD)
            elif op.op == "-":
                ctx.code.append(Opcode.SUBTRACT)
            elif op.op == "*":
                ctx.code.append(Opcode.MULTIPLY)
            elif op.op == "/":
                ctx.code.append(Opcode.DIVIDE)
            else:
                raise TranslatorError("unknown arithmetic operator", op)

        elif type(op) == PVar:
            codegen_read_var(op, ctx)

        else:
            # the given expression contained tokens we don't understand
            raise TranslatorError("unknown token type in expression", op)

def codegen_str(str_token, ctx):
    if type(str_token) != PString:
        raise TranslatorError("expected a string literal to parse", str_token)

    # tries not to include dupe strings
    ctx.code.append(Opcode.LITERAL)
    if str_token.value in ctx.string_table:
        ctx.code.append(ctx.string_table.index(str_token.value))
    else:
        ctx.string_table.append(str_token.value)
        ctx.code.append(len(ctx.string_table))

def codegen_read_var(op, ctx):
    if type(op) != PVar:
        raise TranslatorError("expected a variable", op)
    codegen_name(op.id, ctx)
    ctx.code.append(Opcode.RETRVNUM)


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

        elif code[i] == Opcode.PRINTNUMLIT:
            print addr(i) + " PRINTNUMLIT"

        elif code[i] == Opcode.PRINTSTR:
            print addr(i) + " PRINTSTR"

        elif code[i] == Opcode.PRINTSTRLIT:
            print addr(i) + " PRINTSTRLIT"

        elif code[i] == Opcode.GOTO:
            print addr(i) + " GOTO"

        elif code[i] == Opcode.LITERAL:
            print addr(i) + " LITERAL " + str(code[i+1])
            i += 1
            print addr(i) + "         ^"

        elif code[i] == Opcode.NAME:
            name = ""
            i += 1
            length = code[i]
            for letter in code[i:i+length+1]:
                name += chr(letter)
            print addr(i-1) + " NAME '" + name + "'"
            i += length

        elif code[i] == Opcode.STORENUM:
            print addr(i) + " STORENUM"

        elif code[i] == Opcode.RETRVNUM:
            print addr(i) + " RETRVNUM"

        elif code[i] == Opcode.DELETENUM:
            print addr(i) + " DELETENUM"

        elif code[i] == Opcode.STORESTR:
            print addr(i) + " STORESTR"

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
    LET abc BE 25 + b
    LET q1 BE "Wow"
    LET q2 BE "Amaze"
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

    (code, strings) = translate(ast)
    print "\nCode:"
    pprint.pprint(code)
    print "\nStrings:"
    pprint.pprint(strings)

    print "\nDisassembly:"
    disassemble(code)
