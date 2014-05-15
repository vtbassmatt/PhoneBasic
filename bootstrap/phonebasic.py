#!/usr/bin/env python
from lexer import tokenize
from parser import parse
from translator import translate
from vm import BasicVM

import argparse

parser = argparse.ArgumentParser(description='Run the PhoneBasic compiler.')
parser.add_argument('source', type=file,
                   help='input file')

try:
    args = parser.parse_args()
    prog = args.source.read()
    (code, strings) = translate(parse(tokenize(prog)))

    vm = BasicVM()
    vm.Load(code, strings)
    #vm.SetDebugger(True)
    try:
        vm.Run()
    except Exception, e:
        print e.args

except IOError, e:
    print "couldn't find or open file", e.filename
