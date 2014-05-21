import pprint
import sys
import collections
import struct
from lexer import tokenize
from parser import parse, PClear, PLabel, PLet, PPrint, PIf, PGoto, PInput, PEnd
from parser import PExpr, PVar, PNumber, PArith, PString
from parser import PCall, PCompute, PReturn, PAccept
from vm import Opcode


class TranslatorError(RuntimeError):
    pass


class TContext(object):
    label_table = {}
    string_table = []
    label_fixups = []
    last_label = None
    check_accepts = {}
    check_computes = []
    # by convention, put a magic number at the beginning
    # for this case, "PB01" in ASCII
    code = bytearray([ord("P"), ord("B"), ord("0"), ord("1")])


def translate(ast):
    ctx = TContext()

    for op in ast:
        if type(op) == PLabel:
            codegen_label(op.id, ctx)
            ctx.last_label = op.id

        else:
            codegen_stmt(op, ctx)

    # fix GOTO back-refs
    while len(ctx.label_fixups) > 0:
        (label,addr) = ctx.label_fixups.pop()
        label_addr = ctx.label_table[label]
        val = struct.pack(">h", label_addr)
        ctx.code[addr]   = ord(val[0])
        ctx.code[addr+1] = ord(val[1])

    # verify that all COMPUTEs have the same arg count as their ACCEPTs
    for (compute_label, compute_count) in ctx.check_computes:
        if ctx.check_accepts[compute_label] != compute_count:
            raise TranslatorError("Incorrect argument count for a COMPUTE", compute_label)

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

    elif type(op) == PInput:
        codegen_input(op, ctx)

    elif type(op) == PCall:
        codegen_call(op, ctx)

    elif type(op) == PCompute:
        codegen_compute(op, ctx)

    elif type(op) == PAccept:
        codegen_accept(op, ctx)

    elif type(op) == PReturn:
        codegen_return(op, ctx)

    elif type(op) == PEnd:
        ctx.code.append(Opcode.HALT)

    else:
        ctx.code.append(Opcode.NOOP)

def codegen_call(op, ctx):
    """CALL means move execution to the specified label with a new scope
    of variables. Also, save the place where execution left off, since we'll
    come back here with a RETURN."""
    ctx.code.append(Opcode.PUSHSCOPE)
    codegen_label_address(op.label, ctx)
    ctx.code.append(Opcode.GOSUB)

def codegen_compute(op, ctx):
    """COMPUTE is a CALL plus a set of expression results pushed on the stack
    in reverse order.

    results get assigned back to the original variable."""
    arg_count = 0
    for expr in op.args[::-1]:
        codegen_expr(expr, ctx)
        arg_count += 1

    # save the number of arguments called for later checking
    ctx.check_computes.append( (op.label, arg_count) )

    ctx.code.append(Opcode.PUSHSCOPE)
    codegen_label_address(op.label, ctx)
    ctx.code.append(Opcode.GOSUB)
    # -- execution calls out to the subroutine, and when it returns,
    #    we should have the result on the stack
    codegen_name(op.id, ctx)
    ctx.code.append(Opcode.STORENUM)

def codegen_return(op, ctx):
    """RETURN means destroy the local scope and return execution to where ever
    we came from.

    handle returning a value if necessary"""
    if type(op) != PReturn:
        raise TranslatorError("expected a return statement")

    if op.expr:
        # compute the expression and push it on the stack
        codegen_expr(op.expr, ctx)
    ctx.code.append(Opcode.POPSCOPE)
    # opcode RETURN should be the last thing we call, since it'll immediately
    # send execution elsewhere
    ctx.code.append(Opcode.RETURN)

def codegen_accept(op, ctx):
    """Expect these named arguments to be pushed on the stack in reverse order.

    Meaning, if the arguments are a,b,c - they're on the stack such that
    c pops first and a pops last"""

    # record these variables so we can check their count later
    ctx.check_accepts[ctx.last_label] = 0
    for var in op.rhs:
        codegen_name(var.id, ctx)
        # TODO: allow strings as arguments to subroutines
        ctx.code.append(Opcode.STORENUM)
        ctx.check_accepts[ctx.last_label] += 1

def codegen_if(op, ctx):
    # TODO: bug #1 (add AND, OR, and NOT)
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
    ctx.code.append(Opcode.JUMP)            # jump to it

def codegen_label_address(label, ctx):
    # the +1 accounts for the LITERAL2 op
    ctx.label_fixups.append((label,len(ctx.code)+1))
    codegen_literal2(0, ctx)    # placeholder of 0, will be overwritten later

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

def codegen_input(op, ctx):
    if type(op) != PInput:
        raise TranslatorError("expected an input statement", op)
    for input_var in op.rhs:
        if type(input_var) == PVar:
            codegen_name(input_var.id, ctx)
            ctx.code.append(Opcode.INPUT)
        else:
            raise TranslatorError("expected an input variable", input_var)

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

def codegen_literal2(value, ctx):
    ctx.code.append(Opcode.LITERAL2)
    val = struct.pack(">h", value)
    ctx.code.append(ord(val[0]))
    ctx.code.append(ord(val[1]))

def codegen_float4(value, ctx):
    ctx.code.append(Opcode.FLOAT4)
    val = struct.pack(">f", value)
    ctx.code.append(ord(val[0]))
    ctx.code.append(ord(val[1]))
    ctx.code.append(ord(val[2]))
    ctx.code.append(ord(val[3]))

def codegen_expr(expr_token, ctx):
    # expressions expected in reverse polish notation
    if type(expr_token) != PExpr:
        raise TranslatorError("expected an expression to parse", expr_token)
    for op in expr_token.expr:
        if type(op) == PNumber:
            if "." in op.value:
                codegen_float4(float(op.value), ctx)
            else:
                # TODO: bug #5 (deal with numbers > 65K)
                codegen_literal2(int(op.value), ctx)

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
    ctx.code.append(Opcode.LITERAL1)
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
def disassemble(code, metadata_bytes=4, base_addr=0):
    def addr(a):
        return "{:#04x}".format(a+base_addr)

    i = metadata_bytes
    if i > 0:
        print "Metadata: " + str([chr(a) for a in code[0:i]])

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

        elif code[i] == Opcode.JUMP:
            print addr(i) + " JUMP"

        elif code[i] == Opcode.JUMPIF0:
            print addr(i) + " JUMPIF0"

        elif code[i] == Opcode.LITERAL1:
            try:
                print addr(i) + " LITERAL1", code[i+1], "/", hex(code[i+1])
                i += 1
                print addr(i) + "         ^^^"
            except IndexError:
                print "*** ran out of bytes to process"

        elif code[i] == Opcode.LITERAL2:
            try:
                raw = chr(code[i+1]) + chr(code[i+2])
                tup = struct.unpack(">h", raw)
                val = tup[0]
                print addr(i) + " LITERAL2", val, "/", hex(val)
                i += 2
                print addr(i) + "         ^^^"
            except IndexError:
                print "*** ran out of bytes to process"

        elif code[i] == Opcode.NAME:
            try:
                name = ""
                i += 1
                length = code[i]
                for letter in code[i:i+length+1]:
                    name += chr(letter)
                print addr(i-1) + " NAME '" + name + "'"
                i += length
            except IndexError:
                print "*** ran out of bytes to process"

        elif code[i] == Opcode.STORENUM:
            print addr(i) + " STORENUM"

        elif code[i] == Opcode.RETRV:
            print addr(i) + " RETRV"

        elif code[i] == Opcode.INPUT:
            print addr(i) + " INPUT"

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

        elif code[i] == Opcode.PUSHSCOPE:
            print addr(i) + " PUSHSCOPE"

        elif code[i] == Opcode.POPSCOPE:
            print addr(i) + " POPSCOPE"

        elif code[i] == Opcode.GOSUB:
            print addr(i) + " GOSUB"

        elif code[i] == Opcode.RETURN:
            print addr(i) + " RETURN"

        elif code[i] == Opcode.HALT:
            print addr(i) + " HALT"

        else:
            print addr(i) + " ?? " + str(code[i])

        i += 1


if __name__ == "__main__":
    if len(sys.argv) > 1:
        print "opening file", sys.argv[1]
        with open(sys.argv[1], 'r') as f:
            prog = f.read()
    else:
        from samples import sample_prog as prog

    ast = parse(tokenize(prog))
    print "AST:"
    pprint.pprint(ast)

    (code, strings) = translate(ast)
    #print "\nCode:"
    #pprint.pprint(code)
    print "\nStrings:"
    pprint.pprint(strings)

    print "\nDisassembly:"
    disassemble(code)
