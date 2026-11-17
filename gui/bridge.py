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

  # Format bool to WIN/FAIL 
  def format_symbol_value(self, raw_val):
    if isinstance(raw_val, bool):
      return "WIN" if raw_val else "FAIL"
    
    val_str = str(raw_val)
    lower_str = val_str.strip().lower()
    if lower_str == "true":
      return "WIN"
    elif lower_str == "false":
      return "FAIL"
    return val_str
  
  def get_highlight_tokens(self, source_code):
    highlight_data = []
    if not source_code.strip():
      return highlight_data

    try:
      tokens = lexer(source_code)
      current_idx = 0
      
      for token in tokens:
        lexeme_val = getattr(token, "value", str(token))
        raw_type = getattr(token, "type", None) 
        type_name = getattr(raw_type, "name", str(raw_type)) if raw_type else ""

        tag_category = "identifier"

        # Categorize based on token types
        if type_name in ["HAI", "KTHXBYE", "VISIBLE", "GIMMEH", "AN", "MKAY", "YR"]:
          tag_category = "keyword"
        elif type_name in ["O_RLY", "YA_RLY", "NO_WAI", "OIC", "WTF", "OMG", "OMGWTF"] or lexeme_val in ["O RLY?", "YA RLY", "NO WAI", "OIC"]:
          tag_category = "conditional" 
        elif type_name in ["IM_IN_YR", "IM_OUTTA_YR", "HOW_IZ_I", "IF_U_SAY_SO", "FOUND_YR", "GTFO"]:
          tag_category = "keyword"
        elif type_name in ["TROOF_LIT", "WIN", "FAIL"] or lexeme_val in ["WIN", "FAIL"]:
          tag_category = "boolean"
        elif type_name in ["FUNCTION", "FUNC_NAME"] or "FUNC" in type_name:
          tag_category = "function"
        elif "LIT" in type_name or "NUM" in type_name:
          tag_category = "string" if ("YARN" in type_name or "STR" in type_name) else "number"
        elif "COMMENT" in type_name or type_name in ["BTW", "OBTW"]:
          tag_category = "comment"

        start_idx = source_code.find(lexeme_val, current_idx)
        if start_idx != -1:
          end_idx = start_idx + len(lexeme_val)
          highlight_data.append((tag_category, start_idx, end_idx))
          current_idx = end_idx

    except Exception:
      # Fallback pattern matching for partial typing
      import re
      for match in re.finditer(r"\b(HAI|KTHXBYE|VISIBLE|GIMMEH|I HAS A|ITZ|AN|MKAY|BTW)\b", source_code):
        highlight_data.append(("keyword", match.start(), match.end()))
      for match in re.finditer(r"(O RLY\?|YA RLY|NO WAI|OIC)", source_code):
        highlight_data.append(("conditional", match.start(), match.end()))
      for match in re.finditer(r"\b(WIN|FAIL)\b", source_code):
        highlight_data.append(("boolean", match.start(), match.end()))
      for match in re.finditer(r'".*?"', source_code):
        highlight_data.append(("string", match.start(), match.end()))
      for match in re.finditer(r"BTW.*", source_code):
        highlight_data.append(("comment", match.start(), match.end()))

    return highlight_data

  def execute_code(self, source_code, input_callback=None, output_callback=None):
    tokens_list = []
    symbol_table_list = []
    console_output = ""

    if not source_code or not source_code.strip():
      return tokens_list, symbol_table_list, console_output

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

      def input_with_flush(prompt_text="Enter input:"):
        if output_callback:
          output_callback(f.getvalue())
        value = input_callback(prompt_text)
        f.write(value + "\n")   
        return value

      with redirect_stdout(f):
        interpreter = Interpreter()

        if input_callback:
          if hasattr(interpreter, "set_input_callback"):
            interpreter.set_input_callback(input_with_flush)
          else:
            interpreter.input_callback = input_with_flush

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
        it_raw = (
            interpreter.IT.value
            if hasattr(interpreter.IT, "value")
            else interpreter.IT
        )
        it_val = self.format_symbol_value(it_raw)
        if it_val and it_val != "NOOB":
          symbol_dict["IT"] = it_val

      # Add user-defined variables
      if hasattr(interpreter, "variables") and interpreter.variables:
        for var_name, var_literal in interpreter.variables.items():
          var_raw = (
              var_literal.value
              if hasattr(var_literal, "value")
              else var_literal
          )
          symbol_dict[str(var_name)] = self.format_symbol_value(var_raw)

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
      import traceback
      traceback.print_exc()          
      console_output = f"Runtime Error:\n{type(e).__name__}: {e}"

    return tokens_list, symbol_table_list, console_output