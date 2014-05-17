import os
import pprint
import struct
import collections

def real_clear():
    os.system('cls' if os.name == 'nt' else 'clear')


class VmError(RuntimeError):
    pass


ErrCtx = collections.namedtuple('ErrCtx', ['e', 'loc'])


class Var(object):
    def __init__(self, typ, value):
        self.typ = typ
        self.value = value

    NUMERIC = "numeric"
    STRING = "string"

    def __repr__(self):
        return "<Var:{0}={1}>".format(self.typ, self.value)

class Opcode(object):
    """Opcodes for this virtual machine.

    It is a stack-based machine with only one register, the name register.

    Numbers and strings are stored in tables separate from main memory,
    they're accessed by certain opcodes using the name register.

    In the notes, top of stack is on the right"""

    NOOP        = 0

    # screen stuff
    CLEAR       = 1     # clear the screen
    PRINT       = 2     # [a] => [], string or numeric sent to output
    PRINTNUMLIT = 3     # [a] => [], number 'a' sent to output
    PRINTSTRLIT = 4     # [a] => [], strtab[a] sent to output

    # flow control
    JUMP        = 10    # [addr] => [], jumps to addr
    JUMPIF0     = 11    # [a, addr] => [], jumps to addr if a==0

    # working with data
    LITERAL1    = 20    # [] => [a] where a is the next byte
    LITERAL2    = 21    # [] => [ab] where ab is the next 2 bytes

    FLOAT4      = 25    # [] => [float] where float comes from the next 4 bytes

    # variables
    NAME        = 30    # a = @(IP+1), next 'a' bytes read into name register, IP=IP+a+1
    STORENUM    = 31    # [a] => [], heap[@(namereg)] = a
    DELETENUM   = 32    # heap[@(namereg)] unset
    STORESTR    = 33    # [a] => [], heap[@(namereg)] = strtab[a]
    RETRV       = 34    # [] => [heap[@(namereg)]]
    INPUT       = 35    # await input, store it in heap[@(namereg)]

    # math
    ADD         = 40    # [b, a] => [a+b]
    SUBTRACT    = 41    # [b, a] => [a-b]
    MULTIPLY    = 42    # [b, a] => [a*b]
    DIVIDE      = 43    # [b, a] => [a/b]

    # compare
    EQUAL       = 50    # [b, a] => [1] if a==b, [0] otherwise
    LT          = 51    # [b, a] => [1] if a<b, [0] otherwise
    LTE         = 52    # [b, a] => [1] if a<=b, [0] otherwise
    NEQUAL      = 50    # [b, a] => [1] if a!=b, [0] otherwise
    GT          = 51    # [b, a] => [1] if a>b, [0] otherwise
    GTE         = 52    # [b, a] => [1] if a>=b, [0] otherwise

    # make HALT really obvious
    EOM_HALT    = 254
    HALT        = 255


class BasicVM(object):
    def __init__(self):
        self.code = None
        self.string_table = None
        self.debugger = False

    def SetDebugger(self, debug):
        self.debugger = debug

    def Load(self, code, string_table):
        self.code = code
        self.string_table = string_table
        self.Reset()

    def Reset(self):
        self.IP = 4     # skip metadata
        self.STACK = []
        self.NAME_REG = None
        self.VARS = {}
        self.halted = False

    def Step(self):
        try:
            op = self.code[self.IP]
        except IndexError:
            # ran off the end of memory
            op = Opcode.EOM_HALT

        if self.debugger:
            print "opcode =",op

        if op == Opcode.CLEAR:
            if self.debugger:
                print "{clearscreen}"
            else:
                real_clear()

        elif op == Opcode.LITERAL1:
            var = Var(typ=Var.NUMERIC, value=self.code[self.IP + 1])
            self.STACK.append(var)
            self.IP += 1

        elif op == Opcode.LITERAL2:
            raw = chr(self.code[self.IP+1]) + chr(self.code[self.IP+2])
            val = struct.unpack(">h", raw)
            var = Var(typ=Var.NUMERIC, value=val[0])
            self.STACK.append(var)
            self.IP += 2

        elif op == Opcode.FLOAT4:
            raw = chr(self.code[self.IP+1]) +   \
                    chr(self.code[self.IP+2]) + \
                    chr(self.code[self.IP+3]) + \
                    chr(self.code[self.IP+4])
            val = struct.unpack(">f", raw)
            var = Var(typ=Var.NUMERIC, value=val[0])
            self.STACK.append(var)
            self.IP += 4

        elif op == Opcode.NAME:
            name_len = self.code[self.IP + 1]
            name = "".join([chr(i) for i in
                self.code[self.IP + 2:self.IP + 2 + name_len]])
            self.NAME_REG = name
            self.IP += 1 + name_len

        elif op == Opcode.RETRV:
            name = self.NAME_REG
            if name in self.VARS:
                val = self.VARS[name]
                self.STACK.append(val)
            else:
                raise VmError("RETRV: variable is not defined", ErrCtx(e=name, loc=self.IP))

        elif op == Opcode.INPUT:
            name = self.NAME_REG
            data = raw_input('> ')
            self.VARS[name] = Var(typ=Var.STRING, value=data)

        elif op == Opcode.ADD:
            op2 = self.STACK.pop()
            op1 = self.STACK.pop()
            if op1.typ == Var.NUMERIC and op2.typ == Var.NUMERIC:
                self.STACK.append(Var(typ=Var.NUMERIC, value=(op1.value + op2.value)))
            else:
                raise VmError("ADD: expected both operands to be numeric",
                    ErrCtx(e=(op1,op2), loc=self.IP))

        elif op == Opcode.SUBTRACT:
            op2 = self.STACK.pop()
            op1 = self.STACK.pop()
            if op1.typ == Var.NUMERIC and op2.typ == Var.NUMERIC:
                self.STACK.append(Var(typ=Var.NUMERIC, value=(op1.value - op2.value)))
            else:
                raise VmError("SUBTRACT: expected both operands to be numeric",
                    ErrCtx(e=(op1,op2), loc=self.IP))

        elif op == Opcode.MULTIPLY:
            op2 = self.STACK.pop()
            op1 = self.STACK.pop()
            if op1.typ == Var.NUMERIC and op2.typ == Var.NUMERIC:
                self.STACK.append(Var(typ=Var.NUMERIC, value=(op1.value * op2.value)))
            else:
                raise VmError("MULTIPLY: expected both operands to be numeric",
                    ErrCtx(e=(op1,op2), loc=self.IP))

        elif op == Opcode.DIVIDE:
            op2 = self.STACK.pop()
            op1 = self.STACK.pop()
            if op1.typ == Var.NUMERIC and op2.typ == Var.NUMERIC:
                self.STACK.append(Var(typ=Var.NUMERIC, value=(op1.value / op2.value)))
            else:
                raise VmError("DIVIDE: expected both operands to be numeric",
                    ErrCtx(e=(op1,op2), loc=self.IP))

        elif op == Opcode.EQUAL:
            op1 = self.STACK.pop()
            op2 = self.STACK.pop()
            if op1.typ == op2.typ and op1.value == op2.value:
                self.STACK.append(Var(typ=Var.NUMERIC, value=1))
            else:
                self.STACK.append(Var(typ=Var.NUMERIC, value=0))

        elif op == Opcode.LT:
            op1 = self.STACK.pop()
            op2 = self.STACK.pop()
            if op1.value < op2.value:
                self.STACK.append(Var(typ=Var.NUMERIC, value=1))
            else:
                self.STACK.append(Var(typ=Var.NUMERIC, value=0))

        elif op == Opcode.LTE:
            op1 = self.STACK.pop()
            op2 = self.STACK.pop()
            if op1.value <= op2.value:
                self.STACK.append(Var(typ=Var.NUMERIC, value=1))
            else:
                self.STACK.append(Var(typ=Var.NUMERIC, value=0))

        elif op == Opcode.STORENUM:
            num = self.STACK.pop()
            # TODO: ensure this only works on numerics
            self.VARS[self.NAME_REG] = num

        elif op == Opcode.STORESTR:
            index = self.STACK.pop()
            string = self.string_table[index.value]
            self.VARS[self.NAME_REG] = Var(Var.STRING, string)

        elif op == Opcode.PRINTSTRLIT:
            index = self.STACK.pop()
            print self.string_table[index.value],

        elif op == Opcode.PRINTNUMLIT:
            val = self.STACK.pop()
            print val.value,

        elif op == Opcode.PRINT:
            val = self.STACK.pop()
            print val.value,

        elif op == Opcode.JUMP:
            addr = self.STACK.pop()
            self.IP = addr.value - 1  # the 1 gets added back below

        elif op == Opcode.JUMPIF0:
            addr = self.STACK.pop()
            test = self.STACK.pop()
            if test.value == 0:
                self.IP = addr.value - 1  # the 1 gets added back below

        elif op == Opcode.HALT or op == Opcode.EOM_HALT:
            self.halted = True

        elif op == Opcode.NOOP:
            pass

        else:
            raise VmError("unexpected opcode", ErrCtx(e=op, loc=self.IP))

        self.IP += 1

    def PrintState(self):
        pprint.pprint({
            "IP": self.IP,
            "STACK": self.STACK,
            "NAME_REG": self.NAME_REG,
            "VARs": self.VARS,
            "HALTed": self.halted,
        })

    def Run(self):
        if(self.debugger):
            self.PrintState()
        while not self.halted:
            self.Step()
            if(self.debugger):
                self.PrintState()


if __name__ == "__main__":
    from samples import sample_prog
    from lexer import tokenize
    from parser import parse
    from translator import translate

    (code, strings) = translate(parse(tokenize(sample_prog)))

    vm = BasicVM()
    vm.Load(code, strings)
    #vm.SetDebugger(True)
    vm.Run()
