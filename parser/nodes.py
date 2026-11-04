from dataclasses import dataclass
from typing import Any, Optional
from lexer.tokens import T

class Node: pass

"""
EACH AST NODE IS A CLASS THAT INHERITS FROM NODE
"""
@dataclass
class Program(Node):
    body: list

@dataclass
class Print(Node):
    args: list
    newline: bool = True
    
@dataclass
class Literal(Node):
    value: any
    type: any = None

@dataclass
class Var(Node):
    name: str
    value: any
    type: any = None

@dataclass
class Function(Node):
    body: list
    args: list = None

@dataclass
class FunctionCall(Node):
    name: str
    argv: list
    argc: int

@dataclass 
class Identifier(Node):
    name: str
    type: any = None

@dataclass
class MyReturn(Node):
    value: any
    type: any = None

@dataclass
# name of var and what to reasign it to
class Typecast(Node):
    value: any
    type: any = None

@dataclass
# what value to reassign
class Reassign(Node):
    name: str
    value: any = None
    type: any = None
    
@dataclass
class Operation(Node):
    operand: any
    args: list
    type: any = None

# ==================== CONTROL FLOW NODES ====================

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
@dataclass
class Input(Node):
    var: str
