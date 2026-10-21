from parser import *
from parser.nodes import Identifier, Var

# initialize vars in dictionary
# when IDENT is encountered, check if IDENT in dictionary, if not, throw error


class Interpreter():
    def __init__(self, ast):
        self.ast = ast

        # current working variables dictionary
        self.variables = {}
        self.var_stack = [] 
        # stack of variable scopes, each scope is a dictionary of variables
        # if enter a function, push a new scope onto the stack, if exit a function, pop the scope off the stack
    def run(self, node):
        method = getattr(self, f"exec_{type(node).__name__}")
        return method(node)

    # recursively executes the program node by executing each statement in its body
    def exec_Program(self, n):
        for stmt in n.body: 
            self.run(stmt)


    def exec_Function(self, n):
        self.var_stack.append(self.variables.copy())  # save current scope
        self.variables = {}  # create new scope for function

        # load args into variabales dictionary
        if n.args is not None:
            for var in n.args:
                self.variables[var.name] = var.value

        # recursively executes the function body by executing each statement in its body
        # adding new vars in function's vars
        for stmt in n.body:
            self.run(stmt)
        self.variables = self.var_stack.pop()  # restore previous scope
    
    # executes a print statement by printing the values of its arguments
    def exec_Print(self, n):
        for arg in n.args:
            # if identifier, check if it exists in variables
            # print if it does
            if (isinstance(arg, Identifier)):
                if arg.name not in self.variables:
                    raise RuntimeError(f"Variable {arg.name} is not defined")
                print(self.variables[arg.name].value, end=' ')
            else:
            # print literals
                print(arg.value, end=' ')
        print()

    # assigns a variable
    def exec_Var(self, n):
        self.variables[n.name] = n.value

    # checks if variable exists in the current scope and returns its value
    def exec_Identifier(self, n):
        if n.name not in self.variables:
            raise RuntimeError(f"Variable {n.name} is not defined")
        return self.run(self.variables[n.name])