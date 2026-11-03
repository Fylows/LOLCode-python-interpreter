"""
Comprehensive standalone tests for control_flow module.
Tests:
1. Truthiness evaluation (is_truthy)
2. Control Flow Evaluator (IfThen, SwitchCase, Loop, GTFO)
3. Control Flow Parser (parse_if_then, parse_switch_case, parse_loop, parse_gtfo)

Run from project root:
    python -m control_flow.test_control_flow
"""

import sys
import os
import io

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexer.tokens import T
from lexer.lexer import lexer
from parser.nodes import Literal, Identifier, Print, Operation
from parser.parser import Parser
from interpreter.interpreter import Interpreter
from control_flow.nodes import (
    IfThen,
    MebbeClause,
    SwitchCase,
    CaseClause,
    Loop,
    GTFO,
)
from control_flow.evaluator import ControlFlowEvaluator, is_truthy
from control_flow.flow_parser import (
    parse_if_then,
    parse_switch_case,
    parse_loop,
    parse_gtfo,
)

# --- Patch interpreter with control flow execution methods ---
Interpreter.exec_IfThen = lambda self, n: ControlFlowEvaluator.exec_IfThen(self, n)
Interpreter.exec_SwitchCase = lambda self, n: ControlFlowEvaluator.exec_SwitchCase(self, n)
Interpreter.exec_Loop = lambda self, n: ControlFlowEvaluator.exec_Loop(self, n)
Interpreter.exec_GTFO = lambda self, n: ControlFlowEvaluator.exec_GTFO(self, n)

# Fix for printing in tests: in Python 0 in [True, False] is True, so check type(val) is bool
def _safe_printintg(self, val1):
    if type(val1) is bool:
        print("WIN" if val1 else "FAIL", end=' ')
    else:
        print("NOOB" if val1 is None else val1, end=' ')

Interpreter.printintg = _safe_printintg

passed = 0
failed = 0


def test(name, fn):
    global passed, failed
    try:
        fn()
        print(f"  PASS: {name}")
        passed += 1
    except AssertionError as e:
        print(f"  FAIL: {name} - {e}")
        failed += 1
    except Exception as e:
        print(f"  ERROR: {name} - {type(e).__name__}: {e}")
        failed += 1


def capture_output(fn):
    """Run fn() and return its printed output as a string."""
    old_stdout = sys.stdout
    sys.stdout = buf = io.StringIO()
    try:
        fn()
    finally:
        sys.stdout = old_stdout
    return buf.getvalue()


# =============================================================
# 1. TRUTHINESS TESTS
# =============================================================
print("\n=== 1. TRUTHINESS (is_truthy) ===")


def test_truthy_win():
    assert is_truthy(Literal(True, T.TROOF_TYPE)) is True
test("WIN is truthy", test_truthy_win)


def test_truthy_fail():
    assert is_truthy(Literal(False, T.TROOF_TYPE)) is False
test("FAIL is falsy", test_truthy_fail)


def test_truthy_zero():
    assert is_truthy(Literal(0, T.NUMBR_TYPE)) is False
test("NUMBR 0 is falsy", test_truthy_zero)


def test_truthy_nonzero():
    assert is_truthy(Literal(42, T.NUMBR_TYPE)) is True
test("NUMBR 42 is truthy", test_truthy_nonzero)


def test_truthy_empty_string():
    assert is_truthy(Literal("", T.YARN_TYPE)) is False
test("Empty YARN is falsy", test_truthy_empty_string)


def test_truthy_nonempty_string():
    assert is_truthy(Literal("hello", T.YARN_TYPE)) is True
test("Non-empty YARN is truthy", test_truthy_nonempty_string)


def test_truthy_noob():
    assert is_truthy(None) is False
test("NOOB (None) is falsy", test_truthy_noob)


def test_truthy_float_zero():
    assert is_truthy(Literal(0.0, T.NUMBAR_TYPE)) is False
test("NUMBAR 0.0 is falsy", test_truthy_float_zero)


def test_truthy_float_nonzero():
    assert is_truthy(Literal(3.14, T.NUMBAR_TYPE)) is True
test("NUMBAR 3.14 is truthy", test_truthy_float_nonzero)


# =============================================================
# 2. EVALUATOR - IF-THEN TESTS
# =============================================================
print("\n=== 2. IF-THEN EVALUATION (O RLY?) ===")


def test_if_ya_rly():
    """IT is WIN -> YA RLY block runs"""
    interp = Interpreter()
    interp.IT = Literal(True, T.TROOF_TYPE)

    out = capture_output(lambda: ControlFlowEvaluator.exec_IfThen(interp, IfThen(
        then_block=[Print([Literal("YES", T.YARN_LIT)])],
        mebbe_clauses=[],
        else_block=[Print([Literal("NO", T.YARN_LIT)])],
    )))
    assert "YES" in out and "NO" not in out, f"Expected YES only, got '{out.strip()}'"

test("YA RLY runs when IT is WIN", test_if_ya_rly)


def test_if_no_wai():
    """IT is FAIL -> NO WAI block runs"""
    interp = Interpreter()
    interp.IT = Literal(False, T.TROOF_TYPE)

    out = capture_output(lambda: ControlFlowEvaluator.exec_IfThen(interp, IfThen(
        then_block=[Print([Literal("YES", T.YARN_LIT)])],
        mebbe_clauses=[],
        else_block=[Print([Literal("NO", T.YARN_LIT)])],
    )))
    assert "NO" in out and "YES" not in out, f"Expected NO only, got '{out.strip()}'"

test("NO WAI runs when IT is FAIL", test_if_no_wai)


def test_if_mebbe():
    """IT is FAIL, MEBBE condition is WIN -> MEBBE block runs"""
    interp = Interpreter()
    interp.IT = Literal(False, T.TROOF_TYPE)

    out = capture_output(lambda: ControlFlowEvaluator.exec_IfThen(interp, IfThen(
        then_block=[Print([Literal("YA", T.YARN_LIT)])],
        mebbe_clauses=[
            MebbeClause(
                condition=Literal(True, T.TROOF_TYPE),
                body=[Print([Literal("MEBBE", T.YARN_LIT)])],
            ),
        ],
        else_block=[Print([Literal("NO", T.YARN_LIT)])],
    )))
    assert "MEBBE" in out, f"Expected MEBBE, got '{out.strip()}'"
    assert "YA" not in out and "NO" not in out, f"Expected only MEBBE, got '{out.strip()}'"

test("MEBBE runs when its condition is WIN", test_if_mebbe)


def test_if_no_else():
    """IT is FAIL, no else block -> nothing happens"""
    interp = Interpreter()
    interp.IT = Literal(False, T.TROOF_TYPE)

    out = capture_output(lambda: ControlFlowEvaluator.exec_IfThen(interp, IfThen(
        then_block=[Print([Literal("YES", T.YARN_LIT)])],
        mebbe_clauses=[],
        else_block=None,
    )))
    assert out.strip() == "", f"Expected no output, got '{out.strip()}'"

test("No output when IT is FAIL and no NO WAI", test_if_no_else)


# =============================================================
# 3. EVALUATOR - SWITCH-CASE TESTS
# =============================================================
print("\n=== 3. SWITCH-CASE EVALUATION (WTF?) ===")


def test_switch_match():
    """IT matches OMG 2 -> that case runs"""
    interp = Interpreter()
    interp.IT = Literal(2, T.NUMBR_TYPE)

    out = capture_output(lambda: ControlFlowEvaluator.exec_SwitchCase(interp, SwitchCase(
        cases=[
            CaseClause(Literal(1, T.NUMBR_LIT), [Print([Literal("ONE", T.YARN_LIT)]), GTFO()]),
            CaseClause(Literal(2, T.NUMBR_LIT), [Print([Literal("TWO", T.YARN_LIT)]), GTFO()]),
            CaseClause(Literal(3, T.NUMBR_LIT), [Print([Literal("THREE", T.YARN_LIT)]), GTFO()]),
        ],
        default_block=[Print([Literal("DEFAULT", T.YARN_LIT)])],
    )))
    assert "TWO" in out, f"Expected TWO, got '{out.strip()}'"
    assert "ONE" not in out and "THREE" not in out, f"Expected only TWO, got '{out.strip()}'"

test("Matching OMG case runs", test_switch_match)


def test_switch_default():
    """No match -> OMGWTF runs"""
    interp = Interpreter()
    interp.IT = Literal(99, T.NUMBR_TYPE)

    out = capture_output(lambda: ControlFlowEvaluator.exec_SwitchCase(interp, SwitchCase(
        cases=[
            CaseClause(Literal(1, T.NUMBR_LIT), [Print([Literal("ONE", T.YARN_LIT)]), GTFO()]),
        ],
        default_block=[Print([Literal("DEFAULT", T.YARN_LIT)])],
    )))
    assert "DEFAULT" in out, f"Expected DEFAULT, got '{out.strip()}'"

test("OMGWTF runs when no match", test_switch_default)


def test_switch_fallthrough():
    """OMG 1 matched, no GTFO -> falls through to OMG 2"""
    interp = Interpreter()
    interp.IT = Literal(1, T.NUMBR_TYPE)

    out = capture_output(lambda: ControlFlowEvaluator.exec_SwitchCase(interp, SwitchCase(
        cases=[
            CaseClause(Literal(1, T.NUMBR_LIT), [Print([Literal("ONE", T.YARN_LIT)])]),
            CaseClause(Literal(2, T.NUMBR_LIT), [Print([Literal("TWO", T.YARN_LIT)]), GTFO()]),
        ],
        default_block=None,
    )))
    assert "ONE" in out and "TWO" in out, f"Expected fall-through ONE+TWO, got '{out.strip()}'"

test("Fall-through without GTFO", test_switch_fallthrough)


# =============================================================
# 4. EVALUATOR - LOOP TESTS
# =============================================================
print("\n=== 4. LOOP EVALUATION (IM IN YR) ===")


def test_loop_uppin_til():
    """UPPIN YR i TIL BOTH SAEM i AN 5 -> prints 0,1,2,3,4"""
    interp = Interpreter()
    interp.variables["i"] = Literal(0, T.NUMBR_TYPE)

    condition = Operation(operand=T.EQUAL, args=[Identifier("i", T.IDENT), Literal(5, T.NUMBR_LIT)])
    node = Loop(label="up", operation=T.INC, variable="i",
                condition_type=T.UNTIL, condition=condition,
                body=[Print([Identifier("i", T.IDENT)])])

    out = capture_output(lambda: ControlFlowEvaluator.exec_Loop(interp, node))
    nums = [line.strip() for line in out.strip().split("\n") if line.strip()]
    assert nums == ["0", "1", "2", "3", "4"], f"Expected [0..4], got {nums}"

test("UPPIN with TIL counts 0 to 4", test_loop_uppin_til)


def test_loop_nerfin_til():
    """NERFIN YR i TIL BOTH SAEM i AN 0 -> prints 5,4,3,2,1"""
    interp = Interpreter()
    interp.variables["i"] = Literal(5, T.NUMBR_TYPE)

    condition = Operation(operand=T.EQUAL, args=[Identifier("i", T.IDENT), Literal(0, T.NUMBR_LIT)])
    node = Loop(label="down", operation=T.DEC, variable="i",
                condition_type=T.UNTIL, condition=condition,
                body=[Print([Identifier("i", T.IDENT)])])

    out = capture_output(lambda: ControlFlowEvaluator.exec_Loop(interp, node))
    nums = [line.strip() for line in out.strip().split("\n") if line.strip()]
    assert nums == ["5", "4", "3", "2", "1"], f"Expected [5..1], got {nums}"

test("NERFIN with TIL counts 5 to 1", test_loop_nerfin_til)


def test_loop_wile():
    """WILE DIFFRINT i AN 3 -> prints 0,1,2"""
    interp = Interpreter()
    interp.variables["i"] = Literal(0, T.NUMBR_TYPE)

    condition = Operation(operand=T.NOT_EQUAL, args=[Identifier("i", T.IDENT), Literal(3, T.NUMBR_LIT)])
    node = Loop(label="w", operation=T.INC, variable="i",
                condition_type=T.WHILE, condition=condition,
                body=[Print([Identifier("i", T.IDENT)])])

    out = capture_output(lambda: ControlFlowEvaluator.exec_Loop(interp, node))
    nums = [line.strip() for line in out.strip().split("\n") if line.strip()]
    assert nums == ["0", "1", "2"], f"Expected [0,1,2], got {nums}"

test("WILE repeats while condition is WIN", test_loop_wile)


def test_loop_gtfo():
    """GTFO inside loop body breaks immediately"""
    interp = Interpreter()
    interp.variables["i"] = Literal(0, T.NUMBR_TYPE)

    node = Loop(label="inf", operation=T.INC, variable="i",
                condition_type=None, condition=None,
                body=[GTFO()])

    ControlFlowEvaluator.exec_Loop(interp, node)
    assert interp.variables["i"].value == 0, f"Expected i=0 (break before inc), got {interp.variables['i'].value}"

test("GTFO breaks loop immediately", test_loop_gtfo)


def test_loop_variable_persists():
    """Loop variable retains its final value after loop ends"""
    interp = Interpreter()
    interp.variables["cnt"] = Literal(0, T.NUMBR_TYPE)

    condition = Operation(operand=T.EQUAL, args=[Identifier("cnt", T.IDENT), Literal(3, T.NUMBR_LIT)])
    node = Loop(label="c", operation=T.INC, variable="cnt",
                condition_type=T.UNTIL, condition=condition,
                body=[])

    ControlFlowEvaluator.exec_Loop(interp, node)
    assert interp.variables["cnt"].value == 3, f"Expected cnt=3, got {interp.variables['cnt'].value}"

test("Loop variable keeps final value after loop", test_loop_variable_persists)


# =============================================================
# 5. PARSER TESTS
# =============================================================
print("\n=== 5. CONTROL FLOW PARSING ===")


def test_parse_if_then_basic():
    code = (
        "O RLY?\n"
        "    YA RLY\n"
        "        VISIBLE \"YES\"\n"
        "    NO WAI\n"
        "        VISIBLE \"NO\"\n"
        "OIC\n"
    )
    tokens = lexer(code)
    parser = Parser(tokens)
    node = parse_if_then(parser)
    assert isinstance(node, IfThen)
    assert len(node.then_block) == 1
    assert node.else_block is not None
    assert len(node.else_block) == 1

test("Parse IF-THEN with YA RLY and NO WAI", test_parse_if_then_basic)


def test_parse_if_then_with_mebbe():
    code = (
        "O RLY?\n"
        "    YA RLY\n"
        "        VISIBLE \"first\"\n"
        "    MEBBE WIN\n"
        "        VISIBLE \"second\"\n"
        "    NO WAI\n"
        "        VISIBLE \"third\"\n"
        "OIC\n"
    )
    tokens = lexer(code)
    parser = Parser(tokens)
    node = parse_if_then(parser)
    assert isinstance(node, IfThen)
    assert len(node.then_block) == 1
    assert len(node.mebbe_clauses) == 1
    assert node.else_block is not None

test("Parse IF-THEN with MEBBE", test_parse_if_then_with_mebbe)


def test_parse_switch_case_basic():
    code = (
        "WTF?\n"
        "    OMG 1\n"
        "        VISIBLE \"one\"\n"
        "        GTFO\n"
        "    OMG 2\n"
        "        VISIBLE \"two\"\n"
        "        GTFO\n"
        "    OMGWTF\n"
        "        VISIBLE \"default\"\n"
        "OIC\n"
    )
    # Temporary mock parse_statement to return GTFO for BREAK token
    tokens = lexer(code)
    parser = Parser(tokens)
    orig_parse_stmt = parser.parse_statement
    def patched_parse_stmt():
        if parser.peek().type == T.BREAK:
            return parse_gtfo(parser)
        return orig_parse_stmt()
    parser.parse_statement = patched_parse_stmt

    node = parse_switch_case(parser)
    assert isinstance(node, SwitchCase)
    assert len(node.cases) == 2
    assert node.default_block is not None

test("Parse SWITCH-CASE with OMG and OMGWTF", test_parse_switch_case_basic)


def test_parse_loop_basic():
    code = (
        "IM IN YR myloop UPPIN YR x TIL BOTH SAEM x AN 10\n"
        "    VISIBLE x\n"
        "IM OUTTA YR myloop\n"
    )
    tokens = lexer(code)
    parser = Parser(tokens)
    node = parse_loop(parser)
    assert isinstance(node, Loop)
    assert node.label == "myloop"
    assert node.operation == T.INC
    assert node.variable == "x"
    assert node.condition_type == T.UNTIL
    assert len(node.body) == 1

test("Parse LOOP with UPPIN and TIL", test_parse_loop_basic)


def test_parse_loop_mismatched_label():
    code = (
        "IM IN YR loopA UPPIN YR x\n"
        "    VISIBLE x\n"
        "IM OUTTA YR loopB\n"
    )
    tokens = lexer(code)
    parser = Parser(tokens)
    try:
        parse_loop(parser)
        assert False, "Expected SyntaxError for mismatched loop label"
    except SyntaxError:
        pass  # Expected!

test("Parse LOOP rejects mismatched end label", test_parse_loop_mismatched_label)


# =============================================================
# SUMMARY
# =============================================================
print(f"\n{'='*40}")
print(f"Results: {passed} passed, {failed} failed")
if failed == 0:
    print("ALL CONTROL_FLOW TESTS PASSED!")
else:
    print("Some tests failed.")
    sys.exit(1)
