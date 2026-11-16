class InterpreterBridge:
  def __init__(self):
    pass

  def execute_code(self, source_code):
    print(source_code)

    # TO-D0: 
    # connect backend

    # dummy data for testing 
    tokens = [("HAI", "Code Delimiter"), ("I HAS A", "Variable Declaration"), ("HAI", "Code Delimiter"), ("HAI", "Code Delimiter"), ("HAI", "Code Delimiter"), ("HAI", "Code Delimiter"), ("HAI", "Code Delimiter"), ("HAI", "Code Delimiter"), ("HAI", "Code Delimiter"), ("HAI", "Code Delimiter"), ("HAI", "Code Delimiter"), ("HAI", "Code Delimiter"), ("HAI", "Code Delimiter"), ("HAI", "Code Delimiter")]
    symbols = [("var", "12"), ("var", "12"), ("var", "12"), ("var", "12"), ("var", "12"), ("var", "12"), ("var", "12"), ("var", "12"), ("var", "12"), ("var", "12"), ("var", "12"), ("var", "12"), ("var", "12"), ("var", "12"), ("var", "12"), ("var", "12"), ("var", "12"), ("var", "12"), ("var", "12"), ("var", "12"), ("var", "12"), ("var", "12"), ("var", "12"), ("var", "12"), ("var", "12"), ("var", "12"), ("var", "12qweuoqwjdoqwejd123412pewpdqdcq")]
    output = "noot noot 12\n"

    return tokens, symbols, output