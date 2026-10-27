## TO DO:
- test files
- move files to its respective files
    - flow_parser.py >> parser/parser.py
    - nodes.py >> parser/nodes.py
    - evaluator.py >> check interpreter.py >> move 

## File Structure

```
control_flow/
├── __init__.py      # Package exports
├── nodes.py         # AST node dataclasses (IfThen, SwitchCase, Loop, GTFO, etc.)
├── flow_parser.py   # Parser methods for control flow statements
├── evaluator.py     # Execution logic, truthiness evaluation, and GTFO interrupts
└── README.md        # Documentation and integration guide
```

### Hook into `parser/parser.py`
In `parser/parser.py`, import the control flow parser methods and nodes:
```python
from control_flow import (
    parse_if_then,
    parse_switch_case,
    parse_loop,
    parse_gtfo,
)
```

In `Parser.parse_statement()`:
```python
    case T.IF:
        return parse_if_then(self)
    case T.SWITCH:
        return parse_switch_case(self)
    case T.LOOP_START:
        return parse_loop(self)
    case T.BREAK:
        return parse_gtfo(self)
```

### Hook into `interpreter/interpreter.py`
In `interpreter/interpreter.py`, import the evaluator methods and nodes:
```python
from control_flow import (
    IfThen,
    SwitchCase,
    Loop,
    GTFO,
    ControlFlowEvaluator,
    exec_if_then,
    exec_switch_case,
    exec_loop,
    exec_gtfo,
)
```

In the `Interpreter` class, add dispatcher methods:
```python
    def exec_IfThen(self, n: IfThen):
        ControlFlowEvaluator.exec_IfThen(self, n)

    def exec_SwitchCase(self, n: SwitchCase):
        ControlFlowEvaluator.exec_SwitchCase(self, n)

    def exec_Loop(self, n: Loop):
        ControlFlowEvaluator.exec_Loop(self, n)

    def exec_GTFO(self, n: GTFO):
        ControlFlowEvaluator.exec_GTFO(self, n)
```