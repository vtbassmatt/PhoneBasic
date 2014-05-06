# PhoneBasic

## Goal

Recapture the magic of QBASIC and TI-Basic on modern smartphone platforms

## Strategy

* Implement a simple, approachable language for beginners inspired by BASIC
* Easy to read and type on a smartphone screen
* Language targets a small, easily-portable VM that can be implemented anywhere
* Stretch: Rewrite the compiler in BASIC so it becomes largely self-hosting

## Language

Start small. We'll need:

* Variables - integer and string at first, decimals later
* Expressions
* Functions
* Simple flow control
* Console input and output
* A small standard library
* Lexical scope
* Comments

### Example Syntax

```
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
```

### Grammar

Based on the TinyBasic syntax. Eliminates GOSUB in favor of pseudo-functions.
Different notion of line labeling. Pseudo-functions have a scope.

```
line = label : CR | statement CR

label = [A-Z1-9][A-Z0-9]*

statement = PRINT expr-list
			IF comp-expr THEN statement
			GOTO label
			INPUT var-list
			LET var BE expression
			COMPUTE var AS label (empty | var-list)
			ACCEPT var-list
			RETURN expression
			CLEAR
			END

expr-list = (string|expression) (, (string|expression) )*

comp-expr = expression relop expression

var-list = var (, var)*

expression = (+|-|empty) term ((+|-) term)*

term = factor ((*|/) factor)*

factor = var | number | (expression)

var = [A-Z][A-Z0-9_]*

number = digit digit*

digit = [0-9]

relop = < | <= | = | != | >= | >
```
