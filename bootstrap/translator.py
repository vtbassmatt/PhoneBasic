import pprint
import collections
from lexer import tokenize
from parser import parse, PClear, PLabel, PLet, PPrint, PIf, PGoto, PInput, PEnd
from parser import PExpr, PVar, PNumber, PArith, PString
from vm import Opcode


class TranslatorError(RuntimeError):
    pass


TContext = collections.namedtuple('TContext',
    ['label_table', 'string_table', 'code', 'label_fixups'])


def translate(ast):
    ctx = TContext(
        label_table = {},
        label_fixups = [],
        string_table = [],
        # by convention, put a magic number at the beginning
        # for this case, "PB01" in ASCII
        code = bytearray([ord("P"), ord("B"), ord("0"), ord("1")])
    )

    for op in ast:
        if type(op) == PLabel:
            codegen_label(op.id, ctx)

        else:
            codegen_stmt(op, ctx)

    # fix GOTO back-refs
    while len(ctx.label_fixups) > 0:
        (label,addr) = ctx.label_fixups.pop()
        label_addr = ctx.label_table[label]
        ctx.code[addr] = label_addr

    return (ctx.code, ctx.string_table)


def codegen_stmt(op, ctx):
    if type(op) == PClear:
        ctx.code.append(Opcode.CLEAR)

    elif type(op) == PGoto:
        codegen_goto(op.id, ctx)

    elif type(op) == PLet:
        codegen_let(op, ctx)

    elif type(op) == PPrint:
        codegen_print(op, ctx)

    elif type(op) == PIf:
        codegen_if(op, ctx)

    elif type(op) == PEnd:
        ctx.code.append(Opcode.HALT)

    else:
        ctx.code.append(Opcode.NOOP)

def codegen_if(op, ctx):
    # TODO: think about whether AND, OR, and NOT are important
    if type(op) != PIf:
        raise TranslatorError("expected an if statement", op)
    codegen_expr(op.expr2, ctx)
    codegen_expr(op.expr1, ctx)
    codegen_compop(op.compop, ctx)
    label = "$IF_" + str(len(ctx.code))
    codegen_label_address(label, ctx)
    ctx.code.append(Opcode.JUMPIF0)
    codegen_stmt(op.stmt, ctx)
    codegen_label(label, ctx)

def codegen_compop(compop, ctx):
    if compop == "=":
        ctx.code.append(Opcode.EQUAL)
    elif compop == "<":
        ctx.code.append(Opcode.LT)
    elif compop == "<=":
        ctx.code.append(Opcode.LTE)
    elif compop == "!=":
        ctx.code.append(Opcode.NEQUAL)
    elif compop == ">":
        ctx.code.append(Opcode.GT)
    elif compop == ">=":
        ctx.code.append(Opcode.GTE)
    else:
        raise TranslatorError("unexpected compare operator", compop)

def codegen_label(label, ctx):
    if label in ctx.label_table:
        raise TranslatorError("label already exists", label)
    ctx.label_table[label] = len(ctx.code)

def codegen_goto(label, ctx):
    codegen_label_address(label, ctx)       # we'll figure out the address later
    ctx.code.append(Opcode.GOTO)            # jump to it

def codegen_label_address(label, ctx):
    ctx.code.append(Opcode.LITERAL)         # push a location on the stack
    ctx.label_fixups.append((label,len(ctx.code)))
    ctx.code.append(99)                     # placeholder

def codegen_print(op, ctx):
    if type(op) != PPrint:
        raise TranslatorError("expected a print statement", op)
    for printable in op.rhs:
        if type(printable) == PString:
            codegen_str(printable, ctx)
            ctx.code.append(Opcode.PRINTSTRLIT)
        elif type(printable) == PExpr:
            codegen_expr(printable, ctx)
            ctx.code.append(Opcode.PRINT)

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
        ctx.code.append(len(ctx.string_table)-1)

def codegen_read_var(op, ctx):
    if type(op) != PVar:
        raise TranslatorError("expected a variable", op)
    codegen_name(op.id, ctx)
    ctx.code.append(Opcode.RETRV)


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

        elif code[i] == Opcode.PRINT:
            print addr(i) + " PRINT"

        elif code[i] == Opcode.PRINTNUMLIT:
            print addr(i) + " PRINTNUMLIT"

        elif code[i] == Opcode.PRINTSTRLIT:
            print addr(i) + " PRINTSTRLIT"

        elif code[i] == Opcode.GOTO:
            print addr(i) + " GOTO"

        elif code[i] == Opcode.JUMPIF0:
            print addr(i) + " JUMPIF0"

        elif code[i] == Opcode.LITERAL:
            print addr(i) + " LITERAL", code[i+1], "/", hex(code[i+1])
            i += 1
            print addr(i) + "         ^^^"

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
            print addr(i) + " RETRV"

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

        elif code[i] == Opcode.EQUAL:
            print addr(i) + " EQUAL"

        elif code[i] == Opcode.LT:
            print addr(i) + " LT"

        elif code[i] == Opcode.LTE:
            print addr(i) + " LTE"

        elif code[i] == Opcode.NEQUAL:
            print addr(i) + " NEQUAL"

        elif code[i] == Opcode.LT:
            print addr(i) + " GT"

        elif code[i] == Opcode.LTE:
            print addr(i) + " GTE"

        elif code[i] == Opcode.HALT:
            print addr(i) + " HALT"

        else:
            print addr(i) + " ?? " + str(code[i])

        i += 1


if __name__ == "__main__":
    from samples import sample_prog

    ast = parse(tokenize(sample_prog))
    print "AST:"
    pprint.pprint(ast)

    (code, strings) = translate(ast)
    #print "\nCode:"
    #pprint.pprint(code)
    print "\nStrings:"
    pprint.pprint(strings)

    print "\nDisassembly:"
    disassemble(code)
