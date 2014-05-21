LET a BE 1
LET b BE 2

PRINT a, b

COMPUTE c AS Test a, b, 3

PRINT a, b

END

Test:
 ACCEPT aa, bb, cc
 PRINT aa, bb, cc
 LET aa BE aa + 1
 PRINT aa, bb, cc
RETURN

// expected:
// 1,2
// 1,2,3
// 2,2,3
// 1,2