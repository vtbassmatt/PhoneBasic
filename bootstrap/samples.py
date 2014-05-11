sample_prog = """CLEAR
top:
LET abc BE 25 + 2
LET a BE 4
PRINT abc
PRINT "abc"
LET q1 BE "Wow"
LET q2 BE "Amaze"
PRINT "Hello world", 27
GOTO bottom
PRINT "Hello compiler"
//IF a < 2 THEN GOTO top
//PRINT "Passed the goto!"
//INPUT a, b
bottom:
END
"""

