import unittest
import itertools
from lexer import tokenize, Token

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


if __name__ == '__main__':
    unittest.main()
