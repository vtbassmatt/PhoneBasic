import unittest
import itertools
from parser import parse, PClear, PLabel, PLet, PPrint, PIf, PGoto, PInput, PEnd
from parser import PExpr, PNumber, PVar
from lexer import Token

class TestParser(unittest.TestCase):
    """
    Basic tests for the parser
    """

    def test_parser(self):
        expect = [
            PClear(),
            PLabel(id='top'),
            PLet(id='a', rhs=PExpr(expr=[PNumber(value='25')])),
            PPrint(rhs=['Hello world', PExpr(expr=[PNumber(value='27')]), '\n']),
            PPrint(rhs=['Hello compiler', '\n']),
            PIf(expr1=PExpr(expr=[PVar(id='a')]), compop='<', expr2=PExpr(expr=[PNumber(value='2')]), stmt=PPrint(rhs=['Less than 2', '\n'])),
            PGoto(id='top'),
            PInput(rhs=['a', 'b']),
            PEnd()
        ]

        actual = parse([
            Token("CLEAR", "CLEAR", 1, 0),

            Token("ID", "top", 3, 0),
            Token("COLON", ":", 3, 3),
            Token("NEWLINE", "\n", 3, 4),

            Token("LET", "LET", 4, 0),
            Token("ID", "a", 4, 4),
            Token("ASSIGN", "BE", 4, 6),
            Token("NUMBER", "25", 4, 9),
            Token("NEWLINE", "\n", 4, 11),

            Token("PRINT", "PRINT", 5, 0),
            Token("STRING", "Hello world", 5, 6),
            Token("COMMA", ",", 5, 19),
            Token("NUMBER", "27", 5, 21),
            Token("NEWLINE", "\n", 5, 23),

            Token("PRINT", "PRINT", 6, 0),
            Token("STRING", "Hello compiler", 6, 6),
            Token("NEWLINE", "\n", 6, 22),

            Token("IF", "IF", 7, 0),
            Token("ID", "a", 7, 3),
            Token("COMPOP", "<", 7, 5),
            Token("NUMBER", "2", 7, 7),
            Token("THEN", "THEN", 7, 10),
            Token("PRINT", "PRINT", 7, 15),
            Token("STRING", "Less than 2", 7, 22),
            Token("NEWLINE", "\n", 7, 33),

            Token("GOTO", "GOTO", 8, 0),
            Token("ID", "top", 8, 5),
            Token("NEWLINE", "\n", 8, 8),

            Token("INPUT", "INPUT", 9, 0),
            Token("ID", "a", 9, 7),
            Token("COMMA", ",", 9, 8),
            Token("ID", "b", 9, 10),
            Token("NEWLINE", "\n", 9, 11),

            Token("END", "END", 20, 0),
        ])

        self.assertEqual(expect, actual)


if __name__ == '__main__':
    unittest.main()
