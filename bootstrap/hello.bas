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

LET a BE 3
LET b BE 2
LET c BE "blob"
LET d BE "4"

PRINT "a+b", a+b
PRINT "b+c", b+c
PRINT "c+d", c+d

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