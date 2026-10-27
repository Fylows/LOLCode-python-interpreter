from ast import Return

from parser import *
from parser.nodes import FunctionCall, Identifier, Literal, Function, MyReturn, Typecast, Expression
from lexer.tokens import KEYWORDS, T  
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
            if isinstance(stmt, MyReturn):
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
                if isinstance(arg, Identifier): # get value of variable if it is an identifier
                    arguments.append(self.evaluate_expression(arg))

                elif isinstance(arg, FunctionCall): # get value of function call if it is a function call
                    raise RuntimeError(f"Function calls are not allowed as arguments to functions. Function {function_var} called with function call as argument.")

                elif isinstance(arg, Typecast): # get value of typecast if it is a typecast
                    arguments.append(self.evaluate_expression(arg))

                elif isinstance(arg, Literal): # get value of literal
                    arguments.append(arg)

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
            if isinstance(stmt, MyReturn): # early return if return statement is encountered
                self.exec_Return(stmt)
                break
            self.run(stmt)
        self.variables = self.var_stack.pop()  # restore previous scope
    
    # executes a print statement by printing the values of its arguments
    def exec_Print(self, n):
        for arg in n.args:
            if isinstance(arg, Typecast):
                self.exec_Typecast(arg)
                print("NOOB" if self.IT.value is None else self.IT.value, end=' ')
            
            # if identifier, check if it exists in variables
            elif isinstance(arg, Identifier):
                # if identifier is a function, or variable is not defined, raise error
                if self.functions.get(arg.name):
                    raise RuntimeError(f"Line: Variable {arg} is a function")
                elif arg.name not in self.variables:
                    raise RuntimeError(f"Variable {arg.name} is not defined")
                
                else:
                    print(f"NOOB" if self.variables[arg.name].value is None else self.variables[arg.name].value, end=' ')
            
            # if function call, execute it and print the value of IT
            elif isinstance(arg, FunctionCall):
                self.exec_FunctionCall(arg)
                print(f"NOOB" if self.IT.value is None else self.IT.value, end = '')

            # printing literals
            elif isinstance(arg, Literal):
                print(f"NOOB" if arg.value is None else arg.value, end=' ')

            elif isinstance(arg, Expression):
                self.exec_ArithOp(arg)
                print(f"NOOB" if self.IT.value is None else self.IT.value, end=' ')

            else:
                raise RuntimeError(f"Cannot print argument of type {type(arg).__name__}")
            print()

    # assigns a variable
    # variables are stored as Literal objects
    def exec_Var(self, n):
        if n.name in self.variables or n.name in self.functions:
            raise RuntimeError(f"Variable {n.name} is already defined")

        if n.type == T.FUNCTION:
            self.functions[n.name] = n.value

        else:
            if (isinstance(n.value, Literal)):
                n.value = n.value.value
            if (isinstance(n.value, FunctionCall)):
                if n.value.name not in self.functions:
                    raise RuntimeError(f"Function {n.value.name} is not defined")
                self.exec_FunctionCall(n.value)
                n.value = self.IT.value
                n.type = self.IT.type
            self.variables[n.name] = Literal(n.value, n.type)

    # for function return values, assigning to IT
    def exec_Return(self, n):
        if n.type == T.NOOB:
            self.IT = Literal(None, T.NOOB)
        else:
            self.IT = self.evaluate_expression(n.value)

    # typecasting is just changing value and type of a literal
    def exec_Typecast(self, n):
        value = self.evaluate_expression(n.value)
        self.IT = self.cast_literal(value, n.type)

    # Reassigning a variable is changing value of a variable
    # and possibly also its type
    def exec_Reassign(self, n):
        if n.name not in self.variables:
            raise RuntimeError(f"Variable {n.name} is not defined")

        value = (
            self.variables[n.name]
            if n.value is None
            else self.evaluate_expression(n.value)
        )
        target_type = n.type if n.value is None else value.type
        self.variables[n.name] = self.cast_literal(value, target_type)

    def exec_ArithOp(self, n):
        print(n)

        left_expr = n.left_expr
        right_expr = n.right_expr

        if isinstance(right_expr, Expression):
            right_expr = self.exec_ArithOp(n.right_expr)

        if isinstance(left_expr, Expression):
            left_expr = self.exec_ArithOp(n.left_expr)
        
        is_div_or_mod = n.operand == T.DIV or n.operand == T.MOD and left_expr.value%right_expr.value!=0
        type = T.NUMBAR if (left_expr.type == T.NUMBAR or right_expr.type == T.NUMBAR) or is_div_or_mod else T.NUMBR

        if n.operand == T.ADD:
            value = Literal(left_expr.value + right_expr.value, type)
            self.IT = value
            return value
         
        if n.operand == T.SUB:
            value = Literal(left_expr.value - right_expr.value, type)
            self.IT = value
            return value
        if n.operand == T.MUL:
            value =  Literal(left_expr.value * right_expr.value, type)
            self.IT = value
            return value
        if n.operand == T.DIV:
            value = Literal(left_expr.value / right_expr.value, type)
            self.IT = value
            return value
        if n.operand == T.MOD:
            value = Literal(left_expr.value % right_expr.value, type)
            self.IT = value
            return value
        if n.operand == T.MAX:
            value = Literal(max(left_expr.value,  right_expr.value), type)
            self.IT = value
            return value
        if n.operand == T.MIN:
            value = Literal(min(left_expr.value,  right_expr.value), type)
            self.IT = value
            return value

    # evaluates an expression and returns the corresponding value
    def evaluate_expression(self, expression):
        if isinstance(expression, Identifier):
            if expression.name not in self.variables:
                raise RuntimeError(f"Variable {expression.name} is not defined")
            return self.variables[expression.name]

        if isinstance(expression, Typecast):
            self.exec_Typecast(expression)
            return self.IT

        if isinstance(expression, FunctionCall):
            self.exec_FunctionCall(expression)
            if not isinstance(self.IT, Literal):
                raise RuntimeError("Function call did not produce a Literal result")
            return self.IT

        if isinstance(expression, Expression):
            self.exec_ArithOp(expression)
            return self.IT

        if isinstance(expression, Literal):
            return expression

        raise RuntimeError(
            f"Cannot evaluate expression of type {type(expression).__name__}"
        )

    # makes a new literal based on the new type
    def cast_literal(self, value, target_type):
        if value.type is T.NOOB:
            return Literal(None, target_type)

        converted = (
            int(value.value)
            if target_type == T.NUMBR
            else float(value.value)
            if target_type == T.NUMBAR
            else str(value.value)
            if target_type == T.YARN
            else "WIN" if bool(value.value) == True else "FAIL" if bool(value.value) == False else None
            if target_type == T.TROOF
            else value.value
        )
        return Literal(converted, target_type)