from lexer.tokens import T, KEYWORDS
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
        body = self.parse_block(T.KTHXBYE)
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
        body = self.parse_block(T.FUNC_END)
        return Var(name, Function(body, args if args else None), T.FUNCTION)

    # parse_statement parses a single statement and returns the corresponding node
    # statement := print_statement | function | var decl | function_call
    def parse_statement(self):
        t: T = self.peek()
        match t.type:
            case T.IDENT:
                return self.parse_reassign()
            case T.TYPECAST:
                return self.parse_typecast()
            case T.VISIBLE:
                return self.parse_print()
            case T.FUNC_START:
                return self.parse_function()
            case T.VAR_DECLARE:
                return self.parse_var_decl()
            case T.RETURN:
                return self.parse_return()
            case T.FUNC_CALL:
                return self.parse_function_call()
            case T.BREAK:
                return self.parse_return() # return the BREAK token
            case _: # default case, no match
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
    # expression := literal |IDENT | NUMBAR | NUMBR | YARN | FUNC_CALL
    def parse_expr(self):
        t: T = self.advance()
        match t.type:
            case (T.NUMBAR | T.NUMBR | T.YARN | T.TROOF):
                val = int(t.value) if t.type == T.NUMBR else float(t.value) if t.type == T.NUMBAR else str(t.value)
                return Literal(val, t.type)
            case T.IDENT:
                return Identifier(t.value, t.type)
            case T.FUNC_CALL:
                return self.parse_function_call()
            case T.TYPECAST:
                self.pos -= 1
                return self.parse_typecast()
            case (T.ADD | T.SUB | T.DIV | T.MUL | T.MOD | T.MAX | T.MIN):                # Arithmetic Operations
                left = self.parse_expr()
                self.expect(T.AN)
                right = self.parse_expr()
                return Expression(operand=t.type, left_expr=left, right_expr=right)
        
        raise SyntaxError(f"Line {t.line}: unexpected {t.type.name} in expression")

    # parse_var_decl parses a variable declaration and returns a Var node
    # var_decl := I HAS A IDENT ITZ expression
    def parse_var_decl(self):
        self.expect(T.VAR_DECLARE)         
        name = self.expect(T.IDENT).value
        if self.peek().type != T.VAR_TYPE:
            return Var(name, None, T.NOOB)
        self.expect(T.VAR_TYPE)

        value = self.parse_expr()
        if isinstance(value, FunctionCall):
            return Var(name, value, T.FUNC_CALL)

        elif isinstance(value, Identifier):
            return Var(name, value.name, value.type)

        return Var(name, value.value, value.type)

    # returns a function call node and the function's name 
    def parse_function_call(self):
        # since function calls can be nested
        if self.peek().type == T.FUNC_CALL:
            self.advance()
        # get function name and args it requires
        name = self.expect(T.IDENT).value
        args = []
        if (self.advance().type == T.YR):
            args.append(self.parse_expr())
            while self.peek().type is not T.MKAY:
                self.expect(T.AN)
                self.expect(T.YR)
                # append var if IDENT, else parse expression (raw value)
                args.append(self.parse_expr())
            self.expect(T.MKAY)
        # make a FunctionCall node with the function name, arg count and arg vector, if any 
        return FunctionCall(name, args if args else None, len(args) if args else 0)

    # Return node is a <val, type>
    # if breaking, return is noob
    def parse_return(self):
        t: T = self.peek()
        if t.type == T.BREAK:
            self.advance()
            return MyReturn(T.NOOB, T.NOOB)
        self.expect(T.RETURN)
        value = self.parse_expr()
        return MyReturn(value, value.type)

    # typecast := MAEK expression A type
    def parse_typecast(self):
        self.expect(T.TYPECAST)
        value = self.parse_expr()
        self.advance() if self.peek().type == T.A else None  # consume A
        type = self.parse_type()
        source = value
        return Typecast(source, type)

    # reassignment is in the form of
    # reassign := IDENT R expression
    def parse_reassign(self):
        var = self.expect(T.IDENT)
        operator = self.advance()
        # if in the form of
        # reassign := IDENT IS NOW A expression A type
        if operator.type == T.REASSIGN:
            if self.peek().type not in (T.NUMBAR, T.NUMBR, T.YARN, T.TROOF):
                raise SyntaxError(
                    f"Line {self.peek().line}: expected NUMBAR, NUMBR, YARN or TROOF, got {self.peek().value}"
                )
            return Reassign(var.value, None, self.parse_type())

        if operator.type != T.VAR_ASSIGN:
            raise SyntaxError(
                f"Line {operator.line}: expected R or IS NOW A, got {operator.type.name}"
            )
    
        value = self.parse_expr()
        
        if isinstance(value, FunctionCall):
            return Reassign(var.value, value, T.FUNCTION)
        return Reassign(var.value, value, value.type)

    def parse_type(self):
        type = self.advance()
        if type.value not in ("NUMBAR", "NUMBR", "YARN", "TROOF"):
            raise SyntaxError(
                f"Line {type.line}: expected NUMBAR, NUMBR, YARN or TROOF, got {type.value}"
            )
        return type.type

    def end_statement(self):
        t = self.peek()
        if t.type != T.NEWLINE:
            raise SyntaxError(
                f"Line {t.line}: Expected end of line, got {t.type.name}"
            )
        self.skip_newlines()

    def parse_block(self, end_token):
        self.skip_newlines()
        body = []
        while self.peek().type != end_token:
            if self.peek().type == T.EOF:
                raise SyntaxError(
                    f"Line {self.peek().line}: Reached end of file, expected {end_token.name}"
                )
            body.append(self.parse_statement())
            self.end_statement()
        self.expect(end_token)
        return body
