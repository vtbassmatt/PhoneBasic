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


if __name__ == '__main__':
    unittest.main()
