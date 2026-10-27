"""
Parser implementation for LOLCode Control Flow statements:
- IF-THEN / ELSE (O RLY?, YA RLY, MEBBE, NO WAI, OIC)
- SWITCH-CASE (WTF?, OMG, OMGWTF, OIC)
- LOOPS (IM IN YR <label> <UPPIN|NERFIN> YR <var> [TIL|WILE <expr>], IM OUTTA YR <label>)
- BREAK (GTFO)
"""

from lexer.tokens import T
from control_flow.nodes import (
    IfThen,
    MebbeClause,
    SwitchCase,
    CaseClause,
    Loop,
    GTFO,
)


class ControlFlowParser:
    """
    Provides parser methods for LOLCode control flow constructs.
    Can be used directly or composed with the main Parser.
    """

    def __init__(self, parser):
        self.parser = parser

    def parse_statement_block_until(self, stop_token_types: tuple[T, ...]) -> list:
        """
        Parses a sequence of statements until one of the stop_token_types is peeked.
        Does not consume the stop token.
        """
        body = []
        self.parser.skip_newlines()
        while self.parser.peek().type not in stop_token_types:
            if self.parser.peek().type == T.EOF:
                expected = ", ".join(t.name for t in stop_token_types)
                raise SyntaxError(
                    f"Line {self.parser.peek().line}: Reached EOF, expected one of [{expected}]"
                )
            stmt = self.parser.parse_statement()
            if stmt is not None:
                body.append(stmt)
            self.parser.end_statement()
            self.parser.skip_newlines()
        return body

    def parse_if_then(self) -> IfThen:
        """
        Parses an IF-THEN statement:
            O RLY?
                YA RLY
                    <then_block>
                [MEBBE <expr>
                    <mebbe_block>...]
                [NO WAI
                    <else_block>]
            OIC
        """
        self.parser.expect(T.IF)  # O RLY?
        self.parser.end_statement()
        self.parser.skip_newlines()

        self.parser.expect(T.THEN)  # YA RLY
        self.parser.end_statement()
        self.parser.skip_newlines()

        # Parse YA RLY block until MEBBE, NO WAI, or OIC
        then_block = self.parse_statement_block_until((T.ELIF, T.ELSE, T.ENDIF))

        # Parse any MEBBE clauses
        mebbe_clauses = []
        while self.parser.peek().type == T.ELIF:
            self.parser.advance()  # consume MEBBE
            mebbe_cond = self.parser.parse_expr()
            self.parser.end_statement()
            self.parser.skip_newlines()
            mebbe_body = self.parse_statement_block_until((T.ELIF, T.ELSE, T.ENDIF))
            mebbe_clauses.append(MebbeClause(condition=mebbe_cond, body=mebbe_body))

        # Parse optional NO WAI (else) block
        else_block = None
        if self.parser.peek().type == T.ELSE:
            self.parser.advance()  # consume NO WAI
            self.parser.end_statement()
            self.parser.skip_newlines()
            else_block = self.parse_statement_block_until((T.ENDIF,))

        self.parser.expect(T.ENDIF)  # OIC
        return IfThen(
            then_block=then_block,
            mebbe_clauses=mebbe_clauses,
            else_block=else_block,
        )

    def parse_switch_case(self) -> SwitchCase:
        """
        Parses a SWITCH-CASE statement:
            WTF?
                OMG <literal>
                    <code block>
                [OMG <literal>
                    <code block>...]
                [OMGWTF
                    <code block>]
            OIC
        """
        self.parser.expect(T.SWITCH)  # WTF?
        self.parser.end_statement()
        self.parser.skip_newlines()

        cases = []
        while self.parser.peek().type == T.CASE:
            self.parser.advance()  # consume OMG
            case_val = self.parser.parse_expr()
            self.parser.end_statement()
            self.parser.skip_newlines()
            case_body = self.parse_statement_block_until((T.CASE, T.DEFAULT, T.ENDIF))
            cases.append(CaseClause(value=case_val, body=case_body))

        default_block = None
        if self.parser.peek().type == T.DEFAULT:
            self.parser.advance()  # consume OMGWTF
            self.parser.end_statement()
            self.parser.skip_newlines()
            default_block = self.parse_statement_block_until((T.ENDIF,))

        self.parser.expect(T.ENDIF)  # OIC
        return SwitchCase(cases=cases, default_block=default_block)

    def parse_loop(self) -> Loop:
        """
        Parses a LOOP statement:
            IM IN YR <label> <operation> YR <variable> [TIL|WILE <expression>]
                <code block>
            IM OUTTA YR <label>
        """
        self.parser.expect(T.LOOP_START)  # IM IN YR
        start_label_token = self.parser.expect(T.IDENT)
        start_label = start_label_token.value

        op_token = self.parser.advance()
        if op_token.type not in (T.INC, T.DEC):
            raise SyntaxError(
                f"Line {op_token.line}: Expected UPPIN or NERFIN in loop header, got {op_token.type.name}"
            )
        operation = op_token.type

        self.parser.expect(T.YR)
        var_token = self.parser.expect(T.IDENT)
        var_name = var_token.value

        condition_type = None
        condition = None
        if self.parser.peek().type in (T.UNTIL, T.WHILE):
            cond_token = self.parser.advance()
            condition_type = cond_token.type
            condition = self.parser.parse_expr()

        self.parser.end_statement()
        self.parser.skip_newlines()

        body = self.parse_statement_block_until((T.LOOP_END,))

        self.parser.expect(T.LOOP_END)  # IM OUTTA YR
        end_label_token = self.parser.expect(T.IDENT)
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
        """
        Parses a GTFO (break) statement.
        """
        self.parser.expect(T.BREAK)
        return GTFO()


# Standalone parser helper functions
def parse_if_then(parser) -> IfThen:
    return ControlFlowParser(parser).parse_if_then()


def parse_switch_case(parser) -> SwitchCase:
    return ControlFlowParser(parser).parse_switch_case()


def parse_loop(parser) -> Loop:
    return ControlFlowParser(parser).parse_loop()


def parse_gtfo(parser) -> GTFO:
    return ControlFlowParser(parser).parse_gtfo()
