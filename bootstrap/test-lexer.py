import unittest
import itertools
from lexer import tokenize, Token, LexerError

class TestTokenize(unittest.TestCase):
    """
    Basic tests for the lexer
    """

    def test_numbers(self):
        expect = [
            Token("NUMBER", "1",   1, 0),
            Token("NUMBER", "2",   1, 2),
            Token("NUMBER", "3.2", 1, 4),
            Token("NUMBER", "0.1", 1, 8),
            Token("NUMBER", "-5",  1, 12),
        ]
        tokens = tokenize("1 2 3.2 0.1 -5")
        for (token, ex) in itertools.izip(tokens, expect):
            self.assertEqual(token.typ, ex.typ)
            self.assertEqual(token.value, ex.value)
            self.assertEqual(token.line, ex.line)
            self.assertEqual(token.column, ex.column)


    def test_strings(self):
        expect = [
            Token("STRING", "I'm sorry, Dave",       1, 0),
            Token("STRING", "Open the pod bay door", 1, 18),
        ]
        tokens = tokenize("\"I'm sorry, Dave\" \"Open the pod bay door\"")
        for (token, ex) in itertools.izip(tokens, expect):
            self.assertEqual(token.typ, ex.typ)
            self.assertEqual(token.value, ex.value)
            self.assertEqual(token.line, ex.line)
            self.assertEqual(token.column, ex.column)


    def test_assignment(self):
        expect = [
            Token("LET", "LET", 1, 0),
            Token("ID", "a", 1, 4),
            Token("ASSIGN", "BE", 1, 6),
            Token("NUMBER", "25", 1, 9),
        ]
        tokens = tokenize("LET a BE 25")
        for (token, ex) in itertools.izip(tokens, expect):
            self.assertEqual(token.typ, ex.typ)
            self.assertEqual(token.value, ex.value)
            self.assertEqual(token.line, ex.line)
            self.assertEqual(token.column, ex.column)


    def test_comment(self):
        expect = [
            Token("COMMENT", "//comment", 1, 0),
            Token("NEWLINE", "\n", 1, 9),
            Token("STRING", "not a comment", 2, 0),
        ]
        tokens = tokenize("//comment\n\"not a comment\"")
        for (token, ex) in itertools.izip(tokens, expect):
            self.assertEqual(token.typ, ex.typ)
            self.assertEqual(token.value, ex.value)
            self.assertEqual(token.line, ex.line)
            self.assertEqual(token.column, ex.column)


    def test_badlex(self):
        def inner():
            tokens = tokenize("'not a string'")
            for token in tokens:
                pass

        self.assertRaises(LexerError, inner)


    def test_long(self):
        expect = [
            Token(typ='NEWLINE', value='\n', line=1, column=0),
            Token(typ='COMMENT', value="// We use the 'LET var BE' syntax because = is buried on phone keypads", line=2, column=0),
            Token(typ='NEWLINE', value='\n', line=2, column=70),
            Token(typ='LET', value='LET', line=3, column=0),
            Token(typ='ID', value='A', line=3, column=4),
            Token(typ='ASSIGN', value='BE', line=3, column=6),
            Token(typ='NUMBER', value='1', line=3, column=9),
            Token(typ='NEWLINE', value='\n', line=3, column=10),
            Token(typ='LET', value='LET', line=4, column=0),
            Token(typ='ID', value='B', line=4, column=4),
            Token(typ='ASSIGN', value='BE', line=4, column=6),
            Token(typ='NUMBER', value='0', line=4, column=9),
            Token(typ='NEWLINE', value='\n', line=4, column=10),
            Token(typ='LET', value='LET', line=5, column=0),
            Token(typ='ID', value='GREETING', line=5, column=4),
            Token(typ='ASSIGN', value='BE', line=5, column=13),
            Token(typ='STRING', value='Hello world!', line=5, column=16),
            Token(typ='NEWLINE', value='\n', line=5, column=30),
            Token(typ='PRINT', value='PRINT', line=6, column=0),
            Token(typ='ID', value='GREETING', line=6, column=6),
            Token(typ='NEWLINE', value='\n', line=6, column=14),
            Token(typ='NEWLINE', value='\n', line=7, column=0),
            Token(typ='ID', value='FirstLoop', line=8, column=0),
            Token(typ='COLON', value=':', line=8, column=9),
            Token(typ='NEWLINE', value='\n', line=8, column=10),
            Token(typ='PRINT', value='PRINT', line=9, column=1),
            Token(typ='STRING', value='>', line=9, column=7),
            Token(typ='NEWLINE', value='\n', line=9, column=10),
            Token(typ='INPUT', value='INPUT', line=10, column=1),
            Token(typ='ID', value='B', line=10, column=7),
            Token(typ='NEWLINE', value='\n', line=10, column=8),
            Token(typ='PRINT', value='PRINT', line=11, column=1),
            Token(typ='ID', value='B', line=11, column=7),
            Token(typ='COMMA', value=',', line=11, column=8),
            Token(typ='STRING', value=' - 1 IS ', line=11, column=10),
            Token(typ='COMMA', value=',', line=11, column=20),
            Token(typ='ID', value='B', line=11, column=22),
            Token(typ='ARITHOP', value='-', line=11, column=24),
            Token(typ='ID', value='A', line=11, column=26),
            Token(typ='NEWLINE', value='\n', line=11, column=27),
            Token(typ='IF', value='IF', line=12, column=0),
            Token(typ='ID', value='B', line=12, column=3),
            Token(typ='ID', value='IS', line=12, column=5),
            Token(typ='NUMBER', value='0', line=12, column=8),
            Token(typ='GOTO', value='GOTO', line=12, column=10),
            Token(typ='ID', value='FirstLoop', line=12, column=15),
            Token(typ='NEWLINE', value='\n', line=12, column=24),
            Token(typ='NEWLINE', value='\n', line=13, column=0),
            Token(typ='ID', value='SecondLoop', line=14, column=0),
            Token(typ='COLON', value=':', line=14, column=10),
            Token(typ='NEWLINE', value='\n', line=14, column=11),
            Token(typ='LET', value='LET', line=15, column=0),
            Token(typ='ID', value='I', line=15, column=4),
            Token(typ='ASSIGN', value='BE', line=15, column=6),
            Token(typ='NUMBER', value='1', line=15, column=9),
            Token(typ='NEWLINE', value='\n', line=15, column=10),
            Token(typ='PRINT', value='PRINT', line=16, column=2),
            Token(typ='ID', value='I', line=16, column=8),
            Token(typ='NEWLINE', value='\n', line=16, column=9),
            Token(typ='LET', value='LET', line=17, column=2),
            Token(typ='ID', value='I', line=17, column=6),
            Token(typ='ASSIGN', value='BE', line=17, column=8),
            Token(typ='ID', value='I', line=17, column=11),
            Token(typ='ARITHOP', value='+', line=17, column=13),
            Token(typ='NUMBER', value='1', line=17, column=15),
            Token(typ='NEWLINE', value='\n', line=17, column=16),
            Token(typ='IF', value='IF', line=18, column=0),
            Token(typ='ID', value='I', line=18, column=3),
            Token(typ='COMPOP', value='<', line=18, column=5),
            Token(typ='NUMBER', value='10', line=18, column=7),
            Token(typ='GOTO', value='GOTO', line=18, column=10),
            Token(typ='ID', value='SecondLoop', line=18, column=15),
            Token(typ='NEWLINE', value='\n', line=18, column=25),
            Token(typ='NEWLINE', value='\n', line=19, column=0),
            Token(typ='COMMENT', value="// We could have chosen 'IF B IS 0' to avoid the =", line=20, column=0),
            Token(typ='NEWLINE', value='\n', line=20, column=50),
            Token(typ='COMMENT', value='// but that looked ugly', line=21, column=0),
            Token(typ='NEWLINE', value='\n', line=21, column=23),
            Token(typ='IF', value='IF', line=22, column=0),
            Token(typ='ID', value='B', line=22, column=3),
            Token(typ='COMPOP', value='=', line=22, column=5),
            Token(typ='NUMBER', value='0', line=22, column=7),
            Token(typ='THEN', value='THEN', line=22, column=9),
            Token(typ='PRINT', value='PRINT', line=22, column=14),
            Token(typ='STRING', value='The world makes sense', line=22, column=20),
            Token(typ='NEWLINE', value='\n', line=22, column=43),
            Token(typ='NEWLINE', value='\n', line=23, column=0),
            Token(typ='COMPUTE', value='COMPUTE', line=24, column=0),
            Token(typ='ID', value='C', line=24, column=8),
            Token(typ='AS', value='AS', line=24, column=10),
            Token(typ='ID', value='Plus2', line=24, column=13),
            Token(typ='NUMBER', value='4', line=24, column=19),
            Token(typ='NEWLINE', value='\n', line=24, column=20),
            Token(typ='COMMENT', value="// this will print '6'", line=25, column=0),
            Token(typ='NEWLINE', value='\n', line=25, column=22),
            Token(typ='PRINT', value='PRINT', line=26, column=0),
            Token(typ='ID', value='C', line=26, column=6),
            Token(typ='NEWLINE', value='\n', line=26, column=7),
            Token(typ='NEWLINE', value='\n', line=27, column=0),
            Token(typ='END', value='END', line=28, column=0),
            Token(typ='NEWLINE', value='\n', line=28, column=3),
            Token(typ='NEWLINE', value='\n', line=29, column=0),
            Token(typ='ID', value='Plus2', line=30, column=0),
            Token(typ='COLON', value=':', line=30, column=5),
            Token(typ='NEWLINE', value='\n', line=30, column=6),
            Token(typ='ACCEPT', value='ACCEPT', line=31, column=1),
            Token(typ='ID', value='Var', line=31, column=8),
            Token(typ='NEWLINE', value='\n', line=31, column=11),
            Token(typ='RETURN', value='RETURN', line=32, column=0),
            Token(typ='ID', value='Var', line=32, column=7),
            Token(typ='ARITHOP', value='+', line=32, column=11),
            Token(typ='NUMBER', value='2', line=32, column=13),
            Token(typ='NEWLINE', value='\n', line=32, column=14),
        ]
        tokens = tokenize('''
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
''')
        for (token, ex) in itertools.izip(tokens, expect):
            self.assertEqual(token.typ, ex.typ)
            self.assertEqual(token.value, ex.value)
            self.assertEqual(token.line, ex.line)
            self.assertEqual(token.column, ex.column)


if __name__ == '__main__':
    unittest.main()
