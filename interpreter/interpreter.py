from parser import *
from parser.nodes import Literal
from lexer.tokens import T  
# initialize vars in dictionary
# when IDENT is encountered, check if IDENT in dictionary, if not, throw error


class Interpreter():
    def __init__(self, ast):
        self.ast = ast

        # dictionary of functions, key is function name, value is function body
        self.functions = {}
        # current working variables dictionary
        self.variables = {}

        # stack of variable scopes, each scope is a dictionary of variables
        # if enter a function, push a new scope onto the stack, if exit a function, pop the scope off the stack
        self.var_stack = []

    def run(self, node):
        method = getattr(self, f"exec_{type(node).__name__}")
        return method(node)

    # recursively executes the program node by executing each statement in its body
    def exec_Program(self, n):
        for stmt in n.body: 
            self.run(stmt)

    # function is like program, but it has its own scope
    def exec_FunctionCall(self, n):
        # get function's name and arg names
        function_var = n.name
        if function_var not in self.functions:
            raise RuntimeError(f"Function {function_var} is not defined")

        # store function block to execute
        function = self.functions[function_var]
    
        # get function's expected argument names and the arguments passed to the function
        function_var_names = self.functions[function_var].args if self.functions[function_var].args else []
        arguments = []
        if n.args:
            for arg in n.args:
                if arg.type == T.IDENT: # get value of variable if it is an identifier
                    if arg.value not in self.variables:
                        raise RuntimeError(f"Variable {arg.value} is not defined")
                    arguments.append(self.variables[arg.value])
                elif isinstance(arg, Literal): # get value of literal
                    arguments.append(int(arg.value) if arg.type == T.NUMBR 
                                     else float(arg.value) if arg.type == T.NUMBAR 
                                     else str(arg.value))

        # check of number of arguments passed to function matches number of expected arguments
        if len(arguments) != len(function_var_names):
            raise RuntimeError(f"Function {function_var} expected {len(function_var_names)} arguments but got {len(arguments)}")

        self.var_stack.append(self.variables.copy())  # save current scope
        self.variables = {}  # create new scope for function

        # load args into variables dictionary
        for i, arg in enumerate(arguments):
            self.variables[function_var_names[i]] = arg

        # recursively executes the function body by executing each statement in its body
        for stmt in function.body:
            self.run(stmt)
        self.variables = self.var_stack.pop()  # restore previous scope

        # TODO: return value of function, if any
    
    # executes a print statement by printing the values of its arguments
    def exec_Print(self, n):
        for arg in n.args:
            # if identifier, check if it exists in variables
            # print if it does
            if arg.type == T.IDENT:
                if arg.value not in self.variables:
                    raise RuntimeError(f"Variable {arg.value} is not defined")
                try: # try printing value of variable if it is a Var node, otherwise print the value directly
                    print(self.variables[arg.value].value, end=' ')
                except AttributeError:
                    print(self.variables[arg.value], end=' ')
            else:
            # print literals
                print(arg.value, end=' ')
        print()

    # assigns a variable
    def exec_Var(self, n):
        if n.type == T.FUNCTION:
            self.functions[n.name] = n.value
        else:
            self.variables[n.name] = n.value
