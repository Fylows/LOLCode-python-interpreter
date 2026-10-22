from ast import Return

from parser import *
from parser.nodes import Identifier, Literal, Function
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

        # store return values in IT
        self.IT = T.NOOB

    def run(self, node):
        method = getattr(self, f"exec_{type(node).__name__}")
        return method(node)

    # recursively executes the program node by executing each statement in its body
    def exec_Program(self, n):
        for stmt in n.body: 
             # if return statement is encountered, execute it and break out of the loop
            if isinstance(stmt, Return):
                self.exec_Return(stmt)
                break
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
        if n.argv:
            for arg in n.argv:
                if arg.type == T.IDENT: # get value of variable if it is an identifier
                    try:
                        arguments.append(self.variables[arg.value])
                    except KeyError:
                        raise RuntimeError(f"Variable {arg.value} is not defined")
                elif isinstance(arg, Literal): # get value of literal
                    arguments.append(arg.value)

        # check of number of arguments passed to function matches number of expected arguments
        if len(arguments) != n.argc:
            raise RuntimeError(f"Function {function_var} expected {n.argc} arguments but got {len(arguments)}")

        self.var_stack.append(self.variables.copy())  # save current scope
        self.variables = {}  # create new scope for function

        # load args into variables dictionary
        for i, arg in enumerate(arguments):
            self.variables[function_var_names[i]] = arg

        # recursively executes the function body by executing each statement in its body
        for stmt in function.body:
            self.run(stmt)
        self.variables = self.var_stack.pop()  # restore previous scope
    
    # executes a print statement by printing the values of its arguments
    def exec_Print(self, n):
        for arg in n.args:
            # if identifier, check if it exists in variables
            if isinstance(arg, Identifier):
                # if identifier is a function, raise error
                if self.functions.get(arg.name):
                    raise RuntimeError(f"Variable {arg.name} is a function")
                try:
                    print(self.variables[arg.name].value, end=' ')
                except KeyError:
                    raise RuntimeError(f"Variable {arg.name} is not defined")
        
            # if function call, execute it and print the value of IT
            elif arg.type == T.FUNCTION:
                self.run(arg)
                print(self.IT, end = '')
            else:
                # for printing literals
                print(arg.value, end=' ')
            print()

    # assigns a variable
    def exec_Var(self, n):
        if n.type == T.FUNCTION:
            self.functions[n.name] = n.value
        else:
            self.variables[n.name] = n.value

    # for function return values, assigning to IT
    def exec_Return(self, n):
        if n.type == T.NOOB:
            self.IT = T.NOOB
        elif n.value.type == T.IDENT:
            if n.value.name not in self.variables:
                raise RuntimeError(f"Variable {n.value.name} is not defined")
            self.IT = self.variables[n.value.name].value
        else:
            self.IT = n.value.value
