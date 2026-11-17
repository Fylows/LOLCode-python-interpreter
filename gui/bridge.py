import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
if root_dir not in sys.path:
  sys.path.insert(0, root_dir)

from lexer.lexer import lexer
from parser.parser import Parser
from interpreter.interpreter import Interpreter
import io
from contextlib import redirect_stdout

class InterpreterBridge:

  def __init__(self):
    pass

  def get_friendly_classification(self, token_type):
    if not token_type:
      return "Token"

    name = getattr(token_type, "name", str(token_type))

    mapping = {
        "HAI": "Code Delimiter",
        "KTHXBYE": "Code Delimiter",
        "VAR_DECLARE": "Variable Declaration",
        "VAR_TYPE": "Variable Assignment",
        "VAR_ASSIGN": "Variable Assignment",
        "IDENT": "Variable Identifier",
        "NUMBR_LIT": "Literal",
        "NUMBAR_LIT": "Literal",
        "YARN_LIT": "Literal",
        "TROOF_LIT": "Literal",
        "VISIBLE": "Output Keyword",
        "VISIBLE_CONCAT": "String Delimiter",
        "NEWLINE": "Newline",
    }

    return mapping.get(name, name.replace("_", " ").title())

  def execute_code(self, source_code):
    tokens_list = []
    symbol_table_list = []
    console_output = ""

    try:
      # Run Lexer
      tokens = lexer(source_code)
      for token in tokens:
        lexeme_val = getattr(token, "value", str(token))
        raw_type = getattr(token, "type", None)
        classification_name = self.get_friendly_classification(raw_type)
        tokens_list.append((lexeme_val, classification_name))

      # Run Parser
      parser = Parser(tokens)
      ast = parser.parse_program()

      # Run Interpreter
      f = io.StringIO()
      with redirect_stdout(f):
        interpreter = Interpreter()
        if len(ast) > 2 and ast[2]:
          interpreter.run(ast[2])  # Functions
        if len(ast) > 1 and ast[1]:
          interpreter.run(ast[1])  # Variables
        if len(ast) > 0 and ast[0]:
          interpreter.run(ast[0])  # Main program

      console_output = f.getvalue()
      if not console_output:
        console_output = "Execution finished successfully."

      symbol_dict = {}

      # Add implicit 'IT' variable if it holds a value
      if hasattr(interpreter, "IT") and interpreter.IT is not None:
        it_val = (
            str(interpreter.IT.value)
            if hasattr(interpreter.IT, "value")
            else str(interpreter.IT)
        )
        if it_val and it_val != "NOOB":
          symbol_dict["IT"] = it_val

      # Add user-defined variables
      if hasattr(interpreter, "variables") and interpreter.variables:
        for var_name, var_literal in interpreter.variables.items():
          val_str = (
              str(var_literal.value)
              if hasattr(var_literal, "value")
              else str(var_literal)
          )
          symbol_dict[str(var_name)] = val_str

      # Add defined functions from interpreter.functions
      if hasattr(interpreter, "functions") and interpreter.functions:
        for fxn_name, fxn_obj in interpreter.functions.items():
          args_list = getattr(fxn_obj, "args", [])
          args_str = ", ".join(args_list) if args_list else "none"
          symbol_dict[str(fxn_name)] = f"Function (Params: {args_str})"

      # Convert dictionary back to list format for the treeview
      for identifier, val in symbol_dict.items():
        symbol_table_list.append((identifier, val))

    except Exception as e:
      console_output = f"Runtime Error:\n{str(e)}"

    return tokens_list, symbol_table_list, console_output