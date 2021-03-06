// We use the 'LET var BE' syntax because = is buried on phone keypads
//LET A BE 1
//LET B BE 0
//LET GREETING BE "Hello world!"
//PRINT GREETING

//FirstLoop:
// PRINT ">"
// INPUT B
// PRINT B, " - 1 IS ", B - A
//IF B = 0 THEN GOTO FirstLoop

PRINT "What is your name?"
INPUT name
PRINT "Hello", name

PRINT "Enter your birth year followed by your birth month"
INPUT year, month
PRINT "You were born in", month, year

LET a BE 3
LET b BE 2

PRINT "a,b", a, b
PRINT "a+b", a+b
PRINT "a-b", a-b
PRINT "a*b", a*b
PRINT "a/b", a/b

LET a BE 3.0
LET b BE 2

PRINT "a,b", a, b
PRINT "a+b", a+b
PRINT "a-b", a-b
PRINT "a*b", a*b
PRINT "a/b", a/b

//LET I BE 1
//SecondLoop:
//  PRINT I
//  LET I BE I + 1
//IF I < 10 THEN GOTO SecondLoop

// We could have chosen 'IF B IS 0' to avoid the =
// but that looked ugly
//IF B = 0 THEN PRINT "The world makes sense"

//COMPUTE C AS Plus2 4
//// this will print '6'
//PRINT C
//
END

//Plus2:
// ACCEPT Var
//RETURN Var + 2