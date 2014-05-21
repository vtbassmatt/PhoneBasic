LET a BE 1
PRINT a

CALL SayHello

PRINT a

COMPUTE C AS Plus2 4
// this will print '6'
PRINT C

END

SayHello:
 PRINT "Hello!"
 LET a BE 2
 PRINT a
RETURN

Plus2:
 ACCEPT argu
RETURN argu + 2

// expected output:
// 1
// Hello
// 2
// 1
// 6
