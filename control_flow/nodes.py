# NOTE TO SELF: MOVE THIS TO NODES.PY bEFORE COMMTING!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

from dataclasses import dataclass
from typing import Any, List, Optional
from parser.nodes import Node
from lexer.tokens import T


@dataclass
class MebbeClause(Node):
    """Represents a MEBBE (else-if) branch in an if-then statement."""
    condition: Any
    body: list


@dataclass
class IfThen(Node):
    """
    Represents an IF-THEN conditional statement:
        <expr (stored in IT)>
        O RLY?
            YA RLY
                <then_block>
            [MEBBE <expr>
                <mebbe_block>...]
            [NO WAI
                <else_block>]
        OIC
    """
    then_block: list
    mebbe_clauses: list
    else_block: Optional[list] = None


@dataclass
class CaseClause(Node):
    """Represents an OMG <literal> case branch in a switch statement."""
    value: Any
    body: list


@dataclass
class SwitchCase(Node):
    """
    Represents a WTF? switch-case statement:
        WTF?
            OMG <literal>
                <case_block>
            [OMGWTF
                <default_block>]
        OIC
    """
    cases: list
    default_block: Optional[list] = None


@dataclass
class Loop(Node):
    """
    Represents a loop statement:
        IM IN YR <label> <operation> YR <variable> [TIL|WILE <expression>]
            <body block>
        IM OUTTA YR <label>
    """
    label: str
    operation: T              # T.INC (UPPIN) or T.DEC (NERFIN)
    variable: str             # Counter variable name
    condition_type: Optional[T] = None  # T.UNTIL (TIL) or T.WHILE (WILE)
    condition: Optional[Any] = None     # Condition expression
    body: list = None


@dataclass
class GTFO(Node):
    """
    Represents a GTFO (break) statement inside a loop or switch-case block.
    """
    pass
