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
        ('NUMBER',  r'(\-)?\d+(\.\d*)?'), # Integer or decimal number
        ('STRING',  r'"([^"])*"'),   # Simple strings (no escape character)
        ('ASSIGN',  r'BE'),          # Assignment operator
        ('ID',      r'[A-Za-z][A-Za-z0-9_]*'),  # Identifiers
        ('COMMENT', r'\/\/.*'),      # Comments
        ('ARITHOP', r'[+*\/\-]'),    # Arithmetic operators
        ('COMPOP',  r'<|<=|=|!=|=>|>'),    # Comparison operators
        ('COLON',   r':'),           # Colon (as in labels)
        ('COMMA',   r','),           # Comma (as in expression lists)
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
            line_start = pos + 1
            line += 1
        elif typ != 'SKIP':
            val = mo.group(typ)
            if typ == 'ID' and val in keywords:
                typ = val
            if typ == 'STRING':
                # remove the surrounding quotes
                val = val[1:-1]
            yield Token(typ, val, line, mo.start()-line_start)
        pos = mo.end()
        mo = get_token(s, pos)
    if pos != len(s):
        raise LexerError('Unexpected character %r on line %d' %(s[pos], line))


if __name__ == "__main__":
    statements = '''
// We use the 'LET var BE' syntax because = is buried on phone keypads
LET A BE 1
LET B BE 0
LET GREETING BE "Hello world!"
PRINT GREETING

FirstLoop:
 PRINT ">"
 INPUT B
 PRINT B, " - 1 IS ", B - A
IF B IS 0 GOTO FirstLoop

SecondLoop:
LET I BE 1
  PRINT I
  LET I BE I + 1
IF I < 10 GOTO SecondLoop

// We could have chosen 'IF B IS 0' to avoid the =
// but that looked ugly
IF B = 0 THEN PRINT "The world makes sense"

COMPUTE C AS Plus2 4
// this will print '6'
PRINT C

END

Plus2:
 ACCEPT Var
RETURN Var + 2
'''

    for token in tokenize(statements):
        print(token)
