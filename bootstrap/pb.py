#!/usr/bin/env python
from lexer import tokenize
from parser import parse
from translator import translate, disassemble
from vm import BasicVM, VmError

import argparse

parser = argparse.ArgumentParser(description='Run the PhoneBasic compiler.')
parser.add_argument('source', type=file,
                   help='input file')
parser.add_argument('--debug', help="enable debugging", action="store_true")

try:
    args = parser.parse_args()
    prog = args.source.read()
    (code, strings) = translate(parse(tokenize(prog)))

    vm = BasicVM()
    vm.Load(code, strings)
    if args.debug:
        vm.SetDebugger(True)
    try:
        vm.Run()
    except VmError, e:
        print "Execution error", e.args
        loc = e.args[1]["loc"]
        disassemble(code[loc-3:loc+3], 0)

except IOError, e:
    print "couldn't find or open file", e.filename
