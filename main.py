from interpreter.interpreter import Interpreter
from parser.parser import Parser
from lexer.lexer import lexer
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <source_file>")
        sys.exit(1)
        
    if (sys.argv[1] == "-h"):
        print_tokens(sys.argv[2])
        sys.exit(1)
        
    src = open(sys.argv[1]).read()
    
    tokens = lexer(src)
    parser = Parser(tokens)
    ast = parser.parse_program()
    print(ast)
    interpreter = Interpreter(ast)
    interpreter.run(ast)

def print_tokens(filename):
    src = open(sys.argv[2]).read()
    tokens = lexer(src)
    for token in tokens:
        print(token)

if __name__ == "__main__":
    main()