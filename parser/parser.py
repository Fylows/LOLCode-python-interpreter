from lexer.tokens import T
from parser.nodes import *

class Parser:
    def __init__(self, tokens: list[T]):
        self.tokens = tokens
        self.pos = 0
        
    # peek returns the current token without advancing the position
    def peek(self):
        return self.tokens[self.pos]

    # advance returns the current token and advances the position
    def advance(self):
        t: T = self.tokens[self.pos]
        self.pos += 1
        return t

    # expect checks if current token is expected type
    def expect(self, token_type: T):
        t: T = self.advance()
        if t.type != token_type:
            raise SyntaxError(f"Line {t.line}: expected {token_type.name}, got {t.type.name}")
        return t
    
    # skip_newlines skips over any newline tokens
    def skip_newlines(self):
        while self.peek().type == T.NEWLINE:
            self.advance()
    
    # entry of parser, parse program parses the entire program and returns a Program node
    def parse_program(self):
        self.skip_newlines()
        self.expect(T.HAI)
        self.skip_newlines()
        body = []
        while self.peek().type != T.KTHXBYE:
            body.append(self.parse_statement())
            self.skip_newlines()
        self.expect(T.KTHXBYE)
        return Program(body)

    # when parsing function add it to a var node with a function type
    def parse_function(self):
        self.advance()
        name = self.expect(T.IDENT).value
        args = []
        if (self.advance().type == T.YR):
            args.append(self.expect(T.IDENT).value)
            while self.peek().type is not T.NEWLINE:
                self.expect(T.AN)
                self.expect(T.YR)
                args.append(self.expect(T.IDENT).value)
        self.skip_newlines()
        body = []
        while self.peek().type != T.FUNC_END:
            body.append(self.parse_statement())
            self.skip_newlines()
        self.expect(T.FUNC_END)
        return Var(name, Function(body, args if args else None))

    # parse_statement parses a single statement and returns the corresponding node
    # statement := print_statement | function | var decl | function_call
    def parse_statement(self):
        t: T = self.peek()
        if t.type == T.VISIBLE:
            return self.parse_print()
        if t.type == T.FUNC_START:
            return self.parse_function()
        if t.type == T.IDENT:
            return self.parse_expr()
        if t.type == T.VAR_DECLARE:
            return self.parse_var_decl()
        if t.type == T.FUNC_CALL:
            return self.parse_function_call()
        else:
            raise SyntaxError(f"Line {t.line}: unexpected token {t.type.name}")
        
    # parse_print parses a print statement and returns a Print node
    # print_statement := VISIBLE expression
    def parse_print(self):
        self.expect(T.VISIBLE)
        # IDEALLY EXPRESSION PARSING HERE
        args = [self.parse_expr()]
        while self.peek().type not in (T.NEWLINE, T.EOF):
            args.append(self.parse_expr())
        return Print(args)

    # parse_expr parses an expression and returns the corresponding node
    # expression := literal |IDENT | NUMBAR | NUMBR | YARN
    def parse_expr(self):
        t: T = self.advance()
        if t.type in (T.NUMBAR, T.NUMBR, T.YARN, T.TROOF):
            return Literal(t.value, t.type)
        if t.type == T.IDENT:
            return t
        raise SyntaxError(f"Line {t.line}: unexpected {t.type.name} in expression")

    # parse_var_decl parses a variable declaration and returns a Var node
    # var_decl := VAR_ASSIGN IDENT expression
    def parse_var_decl(self):
        self.expect(T.VAR_DECLARE)
        name = self.expect(T.IDENT).value
        self.expect(T.VAR_TYPE)
        value = self.parse_expr()
        return Var(name, value)

    # returns a function call node and the function's name 
    def parse_function_call(self):
        self.advance()
        name = self.expect(T.IDENT).value
        args = []
        if (self.advance().type == T.YR):
            args.append(self.advance() if self.peek().type == T.IDENT else self.parse_expr())
            while self.peek().type is not T.NEWLINE:
                self.expect(T.AN)
                self.expect(T.YR)
                # append var if IDENT, else parse expression (raw value)
                args.append(self.advance() if self.peek().type == T.IDENT else self.parse_expr())
        return FunctionCall(name, args if args else None)