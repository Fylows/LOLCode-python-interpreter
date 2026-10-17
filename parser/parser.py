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
        self.expect(T.HAI)
        self.skip_newlines()
        body = []
        while self.peek().type != T.KTHXBYE:
            body.append(self.parse_statement())
            self.skip_newlines()
        self.expect(T.KTHXBYE)
        return Program(body)

    # parse_statement parses a single statement and returns the corresponding node
    # statement := print_statement
    def parse_statement(self):
        t: T = self.peek()
        if t.type == T.VISIBLE:
            return self.parse_print()
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
        if t.type in (T.IDENT, T.NUMBAR, T.NUMBR, T.YARN):
            return Literal(t.value)
        if t.type == T.IDENT: 
            return Var(t.value)
        raise SyntaxError(f"Line {t.line}: unexpected {t.type.name} in expression")