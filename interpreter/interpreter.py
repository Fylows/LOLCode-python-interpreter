from parser import *

class Interpreter():
    def __init__(self, ast):
        self.ast = ast

    def run(self, node):
        method = getattr(self, f"exec_{type(node).__name__}")
        return method(node)

    # recursively executes the program node by executing each statement in its body
    def exec_Program(self, n):
        for stmt in n.body: self.run(stmt)
        
    # executes a print statement by printing the values of its arguments
    def exec_Print(self, n):
        for arg in n.args:
            if arg.value is None:
                raise RuntimeError(f"Variable {arg.name} is not defined")
            print(arg.value, end=' ')
        print()
        