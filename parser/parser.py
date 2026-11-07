from lexer.tokens import T, LITERALS, TYPES
from parser.nodes import *

class Parser:
    def __init__(self, tokens: list[T]):
        self.tokens = tokens
        self.pos = 0
        self.fxns = []
        self.vars = []
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

    def skip_comments(self):
        self.skip_newlines()
        while self.peek().type in (T.BTW, T.OBTW, T.TLDR, T.ELLIPSIS):
            comment = self.advance()
            if comment.type == T.OBTW:
                while self.peek().type not in (T.TLDR, T.EOF):
                    self.advance()
                if self.peek().type == T.EOF:
                    raise SyntaxError(
                        f"Line {comment.line}: Reached end of file, expected TLDR"
                    )
                self.advance()
            self.skip_newlines()


    ### ===== BNF PARSING RULES ===== ###

    # entry of parser, parse program parses the entire program and returns a Program node
    def parse_program(self):
        body = []
        self.skip_comments()
        self.parse_function()
        self.expect(T.HAI)
        if (self.peek().type in [T.NUMBAR_LIT, T.NUMBR_LIT]):
            if self.peek().value in ["1.0", "1.1", "1.2", "1.3"]:
                self.advance()
            else:
                raise SyntaxError(f"Line {self.peek().line}: expected version 1.0, 1.1, 1.2 or 1.3, got {self.peek().value}")
        
        self.end_statement()
        if (self.peek().type == T.WAZZUP):
            self.advance()
            self.parse_decl()
            self.advance()
        
        body += self.parse_block(T.KTHXBYE)

        self.parse_function()

        return [Program(body), Program(self.vars) if self.vars else None, Program(self.fxns) if self.fxns else None]

    

    # when parsing function add it to a var node with a function type
    def parse_function(self):
        self.skip_newlines()
        if self.peek().type == T.FUNC_START:    
            self.advance()
            name = self.expect(T.IDENT).value
            args = []
            if (self.peek().type == T.YR):
                self.advance()
                args.append(self.expect(T.IDENT).value)
                while self.peek().type != T.NEWLINE:
                    self.expect(T.AN)
                    self.expect(T.YR)
                    args.append(self.expect(T.IDENT).value)
            self.skip_newlines()
            body = self.parse_block(T.FUNC_END)
            self.fxns.append(Var(name, Function(body, args if args else None), T.FUNCTION))
            self.end_statement()
        self.skip_newlines()


    def parse_decl(self):
        self.skip_newlines()
        while self.peek().type != T.BUHBYE:
            self.skip_newlines()
            if self.peek().type == T.EOF:
                raise SyntaxError(
                    f"Line {self.peek().line}: Reached end of file, expected WAZZUP"
                )
            self.skip_comments()
            self.vars.append(self.parse_var_decl())
            self.end_statement()
        self.skip_newlines()
    # parse_statement parses a single statement and returns the corresponding node
    # statement := print_statement | function | var decl | function_call
    def parse_statement(self):
        t: T = self.peek()
        match t.type:
            case T.IDENT | T.IT:
                self.advance()
                if self.peek().type in [T.REASSIGN, T.VAR_ASSIGN]:
                    self.pos -= 1
                    return self.parse_reassign()
                else:
                    self.pos -= 1
                    return self.parse_expr()  
            case T.TYPECAST:
                return self.parse_typecast()
            case T.VISIBLE:
                return self.parse_print()
            case T.FUNC_START:
                return self.parse_function()
            case T.RETURN:
                return self.parse_return()
            case T.FUNC_CALL:
                return self.parse_function_call()
            # --- CONTROL FLOW ---
            case T.IF:
                return self.parse_if_then()
            case T.SWITCH:
                return self.parse_switch_case()
            case T.LOOP_START:
                return self.parse_loop()
            case T.BREAK:
                return self.parse_gtfo()
            case T.INPUT:
                return self.parse_input()
            case _: # default case, no match
                return self.parse_expr()
    # parse_print parses a print statement and returns a Print node
    # print_statement := VISIBLE expression
    def parse_print(self):
        newline = True
        self.expect(T.VISIBLE)
        args = [self.parse_expr()]
        while self.peek().type not in (T.NEWLINE, T.EOF,T.TERM_NEWLINE,T.BTW,T.OBTW,T.TLDR,T.ELLIPSIS):
            if self.peek().type != T.VISIBLE_CONCAT:
                t = self.peek()
                raise SyntaxError(
                    f"Line {t.line}: Expected '+' between VISIBLE arguments"
                )
            self.advance()
            args.append(self.parse_expr())
        if self.peek().type == T.TERM_NEWLINE:
            newline = False
            self.advance()
        return Print(args, newline)

    # parse_expr parses an expression and returns the corresponding node
    # expression := literal |IDENT | NUMBAR | NUMBR | YARN | FUNC_CALL
    def parse_expr(self):
        t: T = self.advance()

        match t.type:
            case t.type if t.type in LITERALS:
                val = int(t.value) if t.type == T.NUMBR_LIT else float(t.value) if t.type == T.NUMBAR_LIT else str(t.value) if t.type == T.YARN_LIT else t.value == "WIN" if t.type == T.TROOF_LIT else None
                return Literal(val, t.type)
            case T.IDENT:
                return Identifier(t.value, t.type)
            case T.FUNC_CALL:
                return self.parse_function_call()
            case T.TYPECAST:
                self.pos -= 1
                return self.parse_typecast()
            # CASE: Single Operand Operations
            case T.NOT:
                return Operation(operand=t.type, args=[self.parse_expr()])
            # CASE: Non-Variadic Operations
            case ( T.ADD | T.SUB | T.DIV | T.MUL | T.MOD | T.MAX | T.MIN | # Arithmetic
                  T.AND | T.OR | T.ONE | # Boolean
                  T.EQUAL | T.NOT_EQUAL): # Equality 
                left = self.parse_expr()
                self.expect(T.AN)
                right = self.parse_expr()
                return Operation(operand=t.type, args=[left,right])
            # CASE: Variadic Operations
            case (T.CONCAT | T.ANY | T.ALL):
                is_concatenation = t.type == T.CONCAT
                args = [self.parse_expr()]
                while self.peek().type == T.AN:
                    self.expect(T.AN)                      
                    args.append(self.parse_expr())
                if not is_concatenation:   
                    self.expect(T.MKAY)                      
                return Operation(operand=t.type, args=args)
            case T.IT:
                return Identifier("IT", T.IT)
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
        
        elif isinstance(value, Typecast):
            return Var(name, value, value.type)
        
        elif isinstance(value, Identifier):
            return Var(name, value.name, value.type)
        
        elif isinstance(value, Literal):
            return Var(name, value.value, value.type)

        elif isinstance(value, Operation):
            return Var(name, value, value.operand)
            

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
        if self.peek().type in (T.IDENT, T.IT):
            var = self.advance()    
        else:
            raise SyntaxError(f"Line {var.line}: expected IDENT/IT, got {var.type.name}")
        operator = self.advance()
        # if in the form of
        # reassign := IDENT IS NOW A expression A type
        if operator.type == T.REASSIGN:
            if self.peek().type not in TYPES:
                raise SyntaxError(
                    f"Line {self.peek().line}: expected NUMBAR, NUMBR, YARN or TROOF, got {self.peek().value}"
                )
            return Reassign(var.value, None, self.parse_type())

    
        value = self.parse_expr()
        
        if isinstance(value, FunctionCall):
            return Reassign(var.value, value, T.FUNCTION)
        return Reassign(var.value, value, value.type)

    def parse_type(self):
        type = self.advance()
        if type.type not in TYPES:
            raise SyntaxError(
                f"Line {type.line}: expected NUMBAR, NUMBR, YARN or TROOF, got {type.value}"
            )
        return type.type

    def parse_input(self):
        self.expect(T.INPUT)
        return Input(self.expect(T.IDENT).value)

    def end_statement(self):
        if self.peek().type in (T.BTW, T.OBTW, T.TLDR, T.ELLIPSIS):
            self.skip_comments()
            return
        t = self.peek()
        if t.type != T.NEWLINE and t.type != T.EOF:
            raise SyntaxError(
                f"Line {t.line}: Expected end of line, got {t.type.name}"
            )
        self.skip_newlines()
        self.skip_comments()

    def parse_block(self, end_token):
        self.skip_comments()
        body = []
        while self.peek().type != end_token:
            if self.peek().type == T.EOF:
                raise SyntaxError(
                    f"Line {self.peek().line}: Reached end of file, expected {end_token.name}"
                )
            self.skip_comments()
            self.parse_function()
            # if the next token is KTHXBYE, we are at the end of the program, so break
            if (self.peek().type == T.KTHXBYE):
                break
            body.append(self.parse_statement())
            self.end_statement()
        self.expect(end_token)
        return body

    def parse_statement_block_until(self, stop_token_types: tuple[T, ...]) -> list:
        body = []
        self.skip_comments()
        while self.peek().type not in stop_token_types:
            if self.peek().type == T.EOF:
                expected = ", ".join(t.name for t in stop_token_types)
                raise SyntaxError(
                    f"Line {self.peek().line}: Reached EOF, expected one of [{expected}]"
                )
            self.skip_comments()
            stmt = self.parse_statement()
            if stmt is not None:
                body.append(stmt)
            self.end_statement()
            self.skip_newlines()
        return body

    def parse_if_then(self) -> IfThen:
        self.expect(T.IF)  # O RLY?
        self.end_statement()
        self.skip_newlines()

        self.expect(T.THEN)  # YA RLY
        self.end_statement()
        self.skip_newlines()

        # Parse YA RLY block until MEBBE, NO WAI, or OIC
        then_block = self.parse_statement_block_until((T.ELIF, T.ELSE, T.ENDIF))

        # Parse any MEBBE clauses
        mebbe_clauses = []
        while self.peek().type == T.ELIF:
            self.advance()  # consume MEBBE
            mebbe_cond = self.parse_expr()
            self.end_statement()
            self.skip_newlines()
            mebbe_body = self.parse_statement_block_until((T.ELIF, T.ELSE, T.ENDIF))
            mebbe_clauses.append(MebbeClause(condition=mebbe_cond, body=mebbe_body))

        # Parse optional NO WAI (else) block
        else_block = None
        if self.peek().type == T.ELSE:
            self.advance()  # consume NO WAI
            self.end_statement()
            self.skip_newlines()
            else_block = self.parse_statement_block_until((T.ENDIF,))

        self.expect(T.ENDIF)  # OIC
        return IfThen(
            then_block=then_block,
            mebbe_clauses=mebbe_clauses,
            else_block=else_block,
        )

    def parse_switch_case(self) -> SwitchCase:
        self.expect(T.SWITCH)  # WTF?
        self.end_statement()
        self.skip_newlines()

        cases = []
        while self.peek().type == T.CASE:
            self.advance()  # consume OMG
            case_val = self.parse_expr()
            self.end_statement()
            self.skip_newlines()
            case_body = self.parse_statement_block_until((T.CASE, T.DEFAULT, T.ENDIF))
            cases.append(CaseClause(value=case_val, body=case_body))

        default_block = None
        if self.peek().type == T.DEFAULT:
            self.advance()  # consume OMGWTF
            self.end_statement()
            self.skip_newlines()
            default_block = self.parse_statement_block_until((T.ENDIF,))

        self.expect(T.ENDIF)  # OIC
        return SwitchCase(cases=cases, default_block=default_block)

    def parse_loop(self) -> Loop:
        self.expect(T.LOOP_START)  # IM IN YR
        start_label_token = self.expect(T.IDENT)
        start_label = start_label_token.value

        op_token = self.advance()
        if op_token.type not in (T.INC, T.DEC):
            raise SyntaxError(
                f"Line {op_token.line}: Expected UPPIN or NERFIN in loop header, got {op_token.type.name}"
            )
        operation = op_token.type

        self.expect(T.YR)
        var_token = self.expect(T.IDENT)
        var_name = var_token.value

        condition_type = None
        condition = None
        if self.peek().type in (T.UNTIL, T.WHILE):
            cond_token = self.advance()
            condition_type = cond_token.type
            condition = self.parse_expr()

        self.end_statement()
        self.skip_newlines()

        body = self.parse_statement_block_until((T.LOOP_END,))

        self.expect(T.LOOP_END)  # IM OUTTA YR
        end_label_token = self.expect(T.IDENT)
        end_label = end_label_token.value

        if start_label != end_label:
            raise SyntaxError(
                f"Line {end_label_token.line}: Loop closing label '{end_label}' "
                f"does not match opening label '{start_label}'"
            )

        return Loop(
            label=start_label,
            operation=operation,
            variable=var_name,
            condition_type=condition_type,
            condition=condition,
            body=body,
        )

    def parse_gtfo(self) -> GTFO:
        self.expect(T.BREAK)
        return GTFO()
