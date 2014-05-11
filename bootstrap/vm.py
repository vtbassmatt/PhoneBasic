import os
import pprint

def real_clear():
    os.system('cls' if os.name == 'nt' else 'clear')


class VmError(RuntimeError):
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
    JUMPIF0     = 11    # [a, addr] => [], jumps to addr if a==0

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

    # compare
    EQUAL       = 50    # [a, b] => [1] if a==b, [0] otherwise

    # make HALT really obvious
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
        self.NUMVARS = {}
        self.STRVARS = {}
        self.halted = False

    def Step(self):
        op = self.code[self.IP]
        if self.debugger:
            print "opcode =",op

        if op == Opcode.CLEAR:
            if self.debugger:
                print "{clearscreen}"
            else:
                real_clear()

        elif op == Opcode.LITERAL:
            self.STACK.append(self.code[self.IP + 1])
            self.IP += 1

        elif op == Opcode.NAME:
            name_len = self.code[self.IP + 1]
            name = "".join([chr(i) for i in
                self.code[self.IP + 2:self.IP + 2 + name_len]])
            self.NAME_REG = name
            self.IP += 1 + name_len

        elif op == Opcode.RETRVNUM:
            name = self.NAME_REG
            if name in self.NUMVARS:
                val = self.NUMVARS[name]
                self.STACK.append(val)
            else:
                raise VmError("variable is not defined", name)

        elif op == Opcode.ADD:
            op1 = self.STACK.pop()
            op2 = self.STACK.pop()
            self.STACK.append(op1 + op2)

        elif op == Opcode.EQUAL:
            op1 = self.STACK.pop()
            op2 = self.STACK.pop()
            if op1 == op2:
                self.STACK.append(1)
            else:
                self.STACK.append(0)

        elif op == Opcode.STORENUM:
            self.NUMVARS[self.NAME_REG] = self.STACK.pop()

        elif op == Opcode.STORESTR:
            index = self.STACK.pop()
            self.STRVARS[self.NAME_REG] = self.string_table[index]

        elif op == Opcode.PRINTSTRLIT:
            index = self.STACK.pop()
            print self.string_table[index],

        elif op == Opcode.PRINTNUMLIT:
            val = self.STACK.pop()
            print val,

        elif op == Opcode.GOTO:
            self.IP = self.STACK.pop() - 1  # the 1 gets added back below

        elif op == Opcode.JUMPIF0:
            addr = self.STACK.pop()
            test = self.STACK.pop()
            if test == 0:
                self.IP = addr - 1  # the 1 gets added back below

        elif op == Opcode.HALT:
            self.halted = True

        else:
            raise VmError("unexpected opcode", op)

        self.IP += 1

    def PrintState(self):
        pprint.pprint({
            "IP": self.IP,
            "STACK": self.STACK,
            "NAME_REG": self.NAME_REG,
            "NUMs": self.NUMVARS,
            "STRs": self.STRVARS,
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
