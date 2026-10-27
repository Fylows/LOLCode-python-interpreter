"""
Control Flow package for LOLCode interpreter.
Handles:
- IF-THEN / ELSE conditional branching (O RLY?, YA RLY, MEBBE, NO WAI, OIC)
- SWITCH-CASE statements (WTF?, OMG, OMGWTF, OIC)
- LOOPS (IM IN YR, UPPIN/NERFIN, TIL/WILE, IM OUTTA YR)
- BREAK control (GTFO)
"""

from control_flow.nodes import (
    IfThen,
    MebbeClause,
    SwitchCase,
    CaseClause,
    Loop,
    GTFO,
)

from control_flow.flow_parser import (
    ControlFlowParser,
    parse_if_then,
    parse_switch_case,
    parse_loop,
    parse_gtfo,
)

from control_flow.evaluator import (
    ControlFlowEvaluator,
    GTFOInterrupt,
    is_truthy,
    exec_if_then,
    exec_switch_case,
    exec_loop,
    exec_gtfo,
)

__all__ = [
    # Nodes
    "IfThen",
    "MebbeClause",
    "SwitchCase",
    "CaseClause",
    "Loop",
    "GTFO",
    # Parser
    "ControlFlowParser",
    "parse_if_then",
    "parse_switch_case",
    "parse_loop",
    "parse_gtfo",
    # Evaluator
    "ControlFlowEvaluator",
    "GTFOInterrupt",
    "is_truthy",
    "exec_if_then",
    "exec_switch_case",
    "exec_loop",
    "exec_gtfo",
]
