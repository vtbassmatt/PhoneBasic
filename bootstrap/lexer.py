# shamelessly borrowed and adapted from
# https://docs.python.org/3/library/re.html#writing-a-tokenizer

import collections
import re

class LexerError(RuntimeError):
    pass

Token = collections.namedtuple('Token', ['typ', 'value', 'line', 'column'])

def tokenize(s):
    keywords = {'IF', 'THEN', 'PRINT', 'GOTO', 'INPUT', 'LET', 'COMPUTE',
        'AS', 'ACCEPT', 'RETURN', 'CLEAR', 'END'}
    token_specification = [
        ('NUMBER',  r'\d+(\.\d*)?'), # Integer or decimal number
        ('ASSIGN',  r'BE'),          # Assignment operator
        ('ID',      r'[A-Za-z][A-Za-z0-9_]*'),  # Identifiers
        ('COMMENT', r'\/\/.*'),      # Comments
        ('OP',      r'[+*\/\-]'),    # Arithmetic operators
        ('NEWLINE', r'\n'),          # Line endings
        ('SKIP',    r'[ \t]'),       # Skip over spaces and tabs
    ]
    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
    get_token = re.compile(tok_regex).match
    line = 1
    pos = line_start = 0
    mo = get_token(s)
    while mo is not None:
        typ = mo.lastgroup
        if typ == 'NEWLINE':
            yield Token(typ, "\n", line, mo.start()-line_start)
            line_start = pos
            line += 1
        elif typ != 'SKIP':
            val = mo.group(typ)
            if typ == 'ID' and val in keywords:
                typ = val
            yield Token(typ, val, line, mo.start()-line_start)
        pos = mo.end()
        mo = get_token(s, pos)
    if pos != len(s):
        raise LexerError('Unexpected character %r on line %d' %(s[pos], line))


if __name__ == "__main__":
    statements = '''
        IF quantity THEN
            LET total BE total + price * quantity
            LET tax BE price * 0.05
        ENDIF
'''

    for token in tokenize(statements):
        print(token)
