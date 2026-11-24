# LOLCODE Python Interpreter


### Project Structure
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

/gui
    app.py # main TKinter IDE application layout and event loops
    bridge.py # connects the ui to the backend interpreter 
    components.py # custom ui widget
```

### Prerequisites/Dependencies:
Before running the interpreter or GUI, make sure **Python 3** and **Tkinter** are installed on your system:
* **Check Python 3:**
```bash
  python3 --version
```

* **Check Tkinter**
```bash
  python3 -m -tkinter
```
(A small test window should open. If you get No module named '_tkinter', install Tkinter using the steps below.)

### Installing Python and Tkinter:
* **MacOS (via Homebrew):**
```bash
brew install python python-tk
```

* **Windows:**

Download and run the installer from [python.org](https://www.python.org) and ensure tcl/tk and IDLE is checked during installation.

* **Ubuntu:**
```bash
sudo apt update
sudo apt install python3 python3-tk
```

### How to Run the Project:
```bash
python3 -m gui.app
```

### References:



[Bernard Jezua LOLCODE Interpreter 2024](https://github.com/bernardjezua/LOLCODE-Interpreter/)

[Tree Walk Interpreter in Java](https://craftinginterpreters.com/a-tree-walk-interpreter.html)
