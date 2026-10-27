"""
Execution and evaluation logic for LOLCode Control Flow statements.
Implements:
- Truthiness evaluation (TROOF, NOOB, NUMBR, NUMBAR, YARN rules)
- If-Then / Else execution (with MEBBE support)
- Switch-Case execution (with fall-through and OMGWTF support)
- Loop execution (UPPIN, NERFIN, TIL, WILE, and label handling)
- GTFO (break) interrupt handling
"""

from lexer.tokens import T
from parser.nodes import Literal
from control_flow.nodes import IfThen, SwitchCase, Loop, GTFO


class GTFOInterrupt(Exception):
    """Exception raised when GTFO (break) is encountered inside a loop or switch-case."""
    pass


def is_truthy(val) -> bool:
    """
    Evaluates LOLCode truthiness according to language specification:
    - NOOB: FAIL
    - TROOF: WIN is true, FAIL is false
    - NUMBR / NUMBAR: 0 and 0.0 are FAIL, all other numerical values are WIN
    - YARN: "" is FAIL, all other strings are WIN
    """
    if val is None or val is T.NOOB:
        return False

    raw_val = val.value if hasattr(val, "value") else val
    val_type = getattr(val, "type", None)

    if raw_val is None or raw_val is T.NOOB:
        return False

    if val_type == T.TROOF:
        return raw_val in (True, "WIN")

    if isinstance(raw_val, bool):
        return raw_val

    if isinstance(raw_val, (int, float)):
        return raw_val != 0

    if isinstance(raw_val, str):
        if raw_val == "" or raw_val == "FAIL":
            return False
        if raw_val == "WIN":
            return True
        try:
            num = float(raw_val)
            return num != 0
        except ValueError:
            return True

    return bool(raw_val)


class ControlFlowEvaluator:
    """
    Evaluator providing execution methods for control flow AST nodes.
    Can be used by the Interpreter to execute IfThen, SwitchCase, Loop, and GTFO nodes.
    """

    @staticmethod
    def exec_IfThen(interpreter, node: IfThen):
        """
        Executes an IF-THEN statement.
        Uses the implicit IT variable to determine which branch to execute.
        """
        # If IT is truthy (can be cast to WIN), execute YA RLY block
        if is_truthy(interpreter.IT):
            for stmt in node.then_block:
                interpreter.run(stmt)
            return

        # Check MEBBE clauses if present; mebbe else if
        if node.mebbe_clauses:
            for mebbe in node.mebbe_clauses:
                cond_val = interpreter.evaluate_expression(mebbe.condition)
                # Store condition result in IT
                interpreter.IT = (
                    cond_val
                    if isinstance(cond_val, Literal)
                    else Literal(cond_val, T.TROOF)
                )
                if is_truthy(cond_val):
                    for stmt in mebbe.body:
                        interpreter.run(stmt)
                    return

        # Otherwise execute NO WAI (else) block if present
        if node.else_block:
            for stmt in node.else_block:
                interpreter.run(stmt)

    @staticmethod
    def exec_SwitchCase(interpreter, node: SwitchCase):
        """
        Executes a SWITCH-CASE statement.
        Compares implicit variable IT to each OMG case.
        Supports fall-through execution until GTFO or OIC.
        Executes OMGWTF if no case matches or if fell through to it.
        """
        it_val = interpreter.IT.value if hasattr(interpreter.IT, "value") else interpreter.IT

        matched = False
        fell_through_to_default = False

        try:
            for case in node.cases:
                case_literal = interpreter.evaluate_expression(case.value)
                case_val = (
                    case_literal.value
                    if hasattr(case_literal, "value")
                    else case_literal
                )

                # Check for match or fallthrough
                if matched or (str(it_val) == str(case_val) or it_val == case_val):
                    matched = True
                    for stmt in case.body:
                        interpreter.run(stmt)

            # If matched without GTFO, it falls through into default block
            fell_through_to_default = matched

            # If no case matched, or execution fell through, execute OMGWTF if present
            if (not matched or fell_through_to_default) and node.default_block is not None:
                if not matched or fell_through_to_default:
                    for stmt in node.default_block:
                        interpreter.run(stmt)

        except GTFOInterrupt:
            # GTFO breaks out of the switch statement
            pass

    @staticmethod
    def exec_Loop(interpreter, node: Loop):
        """
        Executes a LOOP statement:
        1. Check condition (TIL / WILE).
        2. Execute loop body.
        3. Catch GTFOInterrupt to exit cleanly.
        4. Apply operation (UPPIN / NERFIN) to loop variable.
        5. Repeat.
        """
        if node.variable not in interpreter.variables:
            raise RuntimeError(f"Loop variable '{node.variable}' is not defined")

        while True:
            # 1. Condition check before loop iteration
            if node.condition_type and node.condition:
                cond_val = interpreter.evaluate_expression(node.condition)
                cond_truthy = is_truthy(cond_val)

                # TIL repeats while expression is FAIL (stops when WIN)
                if node.condition_type == T.UNTIL and cond_truthy:
                    break

                # WILE repeats while expression is WIN (stops when FAIL)
                if node.condition_type == T.WHILE and not cond_truthy:
                    break

            # 2. Execute loop body
            try:
                for stmt in node.body:
                    interpreter.run(stmt)
            except GTFOInterrupt:
                break

            # 3. Apply operation (UPPIN / NERFIN) to counter variable
            var_literal = interpreter.variables[node.variable]
            current_num = var_literal.value

            # Convert to numerical if needed
            if isinstance(current_num, str):
                current_num = float(current_num) if "." in current_num else int(current_num)

            if node.operation == T.INC:
                new_num = current_num + 1
            elif node.operation == T.DEC:
                new_num = current_num - 1
            else:
                raise RuntimeError(f"Unknown loop operation: {node.operation}")

            target_type = T.NUMBAR if isinstance(new_num, float) else T.NUMBR
            interpreter.variables[node.variable] = Literal(new_num, target_type)

    @staticmethod
    def exec_GTFO(interpreter, node: GTFO):
        """
        Executes a GTFO statement by raising GTFOInterrupt.
        """
        raise GTFOInterrupt()


# Standalone runner functions
def exec_if_then(interpreter, node: IfThen):
    ControlFlowEvaluator.exec_IfThen(interpreter, node)


def exec_switch_case(interpreter, node: SwitchCase):
    ControlFlowEvaluator.exec_SwitchCase(interpreter, node)


def exec_loop(interpreter, node: Loop):
    ControlFlowEvaluator.exec_Loop(interpreter, node)


def exec_gtfo(interpreter, node: GTFO):
    ControlFlowEvaluator.exec_GTFO(interpreter, node)
