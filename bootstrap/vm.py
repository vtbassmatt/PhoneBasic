
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


class BasicVM(object):
    def __init__(self):
        self.code = None
        self.string_table = None

    def Load(self, code, string_table):
        self.code = code
        self.string_table = string_table
        self.Reset()

    def Reset(self):
        self.IP = 0
        self.NAME_REG = None
        self.VARS = {}
        self.halted = False

    def Step(self):
        # TODO
        self.halted = True

    def Run(self):
        while not self.halted:
            self.Step()


if __name__ == "__main__":
    from samples import sample_prog
    from lexer import tokenize
    from parser import parse
    from translator import translate

    (code, strings) = translate(parse(tokenize(sample_prog)))

    vm = BasicVM()
    vm.Load(code, strings)
    vm.Run()
