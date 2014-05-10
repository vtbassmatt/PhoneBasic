import unittest
import itertools
from parser import parse, ParserError
from parser import PClear, PLabel, PLet, PPrint, PIf, PGoto, PInput, PEnd
from parser import PExpr, PNumber, PVar, PArith
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

    def test_expr_parser(self):
        """test the expression parser with a good case"""
        # from the Shunting Yard page on wikipedia:
        # 3 + 4 * 2 / ( 1 - 5 )
        expect = [
            PLet(id='a', rhs=PExpr(expr=[
                PNumber(value='3'),
                PNumber(value='4'),
                PNumber(value='2'),
                PArith(op='*'),
                PNumber(value='1'),
                PNumber(value='5'),
                PArith(op='-'),
                PArith(op='/'),
                PArith(op='+'),
            ])),
        ]

        actual = parse([
            Token("LET", "LET", 4, 0),
            Token("ID", "a", 4, 4),
            Token("ASSIGN", "BE", 4, 6),
            Token("NUMBER", "3", 4, 9),
            Token("ARITHOP", "+", 4, 10),
            Token("NUMBER", "4", 4, 11),
            Token("ARITHOP", "*", 4, 12),
            Token("NUMBER", "2", 4, 13),
            Token("ARITHOP", "/", 4, 14),
            Token("LPAREN", "(", 4, 15),
            Token("NUMBER", "1", 4, 16),
            Token("ARITHOP", "-", 4, 17),
            Token("NUMBER", "5", 4, 18),
            Token("RPAREN", ")", 4, 19),
            Token("NEWLINE", "\n", 4, 20),
        ])

        self.assertEqual(expect, actual)

    def test_expr_mismatch_1(self):
        """paren mismatch 1"""
        # 2 + ( 1 - 5
        def inner():
            parse([
                Token("LET", "LET", 4, 0),
                Token("ID", "a", 4, 4),
                Token("ASSIGN", "BE", 4, 6),
                Token("NUMBER", "2", 4, 9),
                Token("ARITHOP", "+", 4, 10),
                Token("LPAREN", "(", 4, 11),
                Token("NUMBER", "1", 4, 12),
                Token("ARITHOP", "-", 4, 13),
                Token("NUMBER", "5", 4, 14),
                Token("NEWLINE", "\n", 4, 15),
            ])
        self.assertRaises(ParserError, inner)

    def test_expr_mismatch_2(self):
        """paren mismatch 2"""
        # 2 + 1 - 5 )
        def inner():
            parse([
                Token("LET", "LET", 4, 0),
                Token("ID", "a", 4, 4),
                Token("ASSIGN", "BE", 4, 6),
                Token("NUMBER", "2", 4, 9),
                Token("ARITHOP", "+", 4, 10),
                Token("NUMBER", "1", 4, 11),
                Token("ARITHOP", "-", 4, 12),
                Token("NUMBER", "5", 4, 13),
                Token("RPAREN", ")", 4, 14),
                Token("NEWLINE", "\n", 4, 15),
            ])
        self.assertRaises(ParserError, inner)

    def test_expr_mismatch_3(self):
        """paren mismatch 3"""
        # 2 + (( 1 - 5 )
        def inner():
            parse([
                Token("LET", "LET", 4, 0),
                Token("ID", "a", 4, 4),
                Token("ASSIGN", "BE", 4, 6),
                Token("NUMBER", "2", 4, 9),
                Token("ARITHOP", "+", 4, 10),
                Token("LPAREN", "(", 4, 11),
                Token("LPAREN", "(", 4, 12),
                Token("NUMBER", "1", 4, 13),
                Token("ARITHOP", "-", 4, 14),
                Token("NUMBER", "5", 4, 15),
                Token("RPAREN", ")", 4, 11),
                Token("NEWLINE", "\n", 4, 17),
            ])
        self.assertRaises(ParserError, inner)


if __name__ == '__main__':
    unittest.main()
