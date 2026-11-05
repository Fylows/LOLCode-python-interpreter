# LOLCODE Python Interpteter

```
/lexer
    lexer.py # lexer function
    tokens.py # includes token class and keywords

/parser
    nodes.py # nodes for AST
    parser.py # parses input into AST

/interpreter
    interpreter.py # interpreter for walking through AST and executing its nodes

/control_flow
    nodes.py # AST nodes for conditionals, loops, and switches
    flow_parser.py # parser for control flow constructs
    evaluator.py # evaluator for executing control flow logic
```

References:


[Bernard Jezua LOLCODE Interpreter 2024](https://github.com/bernardjezua/LOLCODE-Interpreter/)

[Tree Walk Interpreter in Java](https://craftinginterpreters.com/a-tree-walk-interpreter.html)
