from ast import Return

from parser import *
from parser.nodes import FunctionCall, Identifier, Literal, Function, MyReturn, Typecast, Operation
from lexer.tokens import KEYWORDS, T  
# initialize vars in dictionary
# when IDENT is encountered, check if IDENT in dictionary, if not, throw error


class Interpreter():
    def __init__(self):
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
        if not node:
            return
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
                self.printintg(self.IT.value)
            
            # if identifier, check if it exists in variables
            elif isinstance(arg, Identifier):
                # if identifier is a function, or variable is not defined, raise error
                if self.functions.get(arg.name):
                    raise RuntimeError(f"Line: Variable {arg} is a function")
                elif arg.name not in self.variables:
                    raise RuntimeError(f"Variable {arg.name} is not defined")
                
                else:
                    self.printintg(self.variables[arg.name].value)
            
            # if function call, execute it and print the value of IT
            elif isinstance(arg, FunctionCall):
                self.exec_FunctionCall(arg)
                self.printintg(self.IT.value)

            # printing literals
            elif isinstance(arg, Literal):
                self.printintg(arg.value)

            elif isinstance(arg, Operation):
                self.exec_Ops(arg)
                self.printintg(self.IT.value)

            else:
                raise RuntimeError(f"Cannot print argument of type {type(arg).__name__}")
            if n.newline:
                print()

    # assigns a variable
    # variables are stored as Literal objects
    def exec_Var(self, n):
        if n.name in self.variables or n.name in self.functions:
            raise RuntimeError(f"Variable {n.name} is already defined")

        if n.type == T.FUNCTION:
            self.functions[n.name] = n.value
        elif n.type == T.IDENT:
            if n.value not in self.variables:
                raise RuntimeError(f"Variable {n.value} is not defined")
            self.variables[n.name] = self.variables[n.value]
        else:
            if (isinstance(n.value, Literal)):
                    n.value = n.value
            elif (isinstance(n.value, FunctionCall)):
                if n.value.name not in self.functions:
                    raise RuntimeError(f"Function {n.value.name} is not defined")
                self.exec_FunctionCall(n.value)
                n.value = self.IT.value
                n.type = self.IT.type
            elif (isinstance(n.value, Typecast)):
                self.exec_Typecast(n.value)
                n.value = self.IT.value
                n.type = self.IT.type
            elif (isinstance(n.value, Operation)):
                self.exec_Ops(n.value)
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

    def evaluate_boolean(self, ops, n):
        if n.operand == T.AND:
            value = Literal(ops[0].value and  ops[1].value, T.TROOF_TYPE)
        if n.operand == T.OR:
            value = Literal(ops[0].value or ops[1].value, T.TROOF_TYPE)
        if n.operand == T.NOT:
            value = self.cast_literal(Literal(not ops[0].value, T.TROOF_TYPE), T.TROOF_TYPE) 
        if n.operand == T.ONE:
            value = Literal(ops[0].value ^ ops[1].value, T.TROOF_TYPE)
        self.IT = value
        return value

    def evaluate_arithmetic(self, ops, n):
        is_div_or_mod = n.operand == T.DIV or n.operand == T.MOD and ops[0].value%ops[1].value!=0
        type = T.NUMBAR_TYPE if (ops[0].type == T.NUMBAR_TYPE or ops[1].type == T.NUMBAR_TYPE) or is_div_or_mod else T.NUMBR_TYPE

        if type == T.NUMBAR_TYPE:
            l = float(ops[0].value)
            r = float(ops[1].value)
        else:
            l = int(ops[0].value)
            r = int(ops[1].value)


        if n.operand == T.ADD:
            value = Literal(l + r, type)
        if n.operand == T.SUB:
            value = Literal(l - r, type)
        if n.operand == T.MUL:
            value =  Literal(l * r, type)
        if n.operand == T.DIV:
            value = Literal(l / r, type)
        if n.operand == T.MOD:
            value = Literal(l % r, type)
        if n.operand == T.MAX:
            value = Literal(max(l, r), type)
        if n.operand == T.MIN:
            value = Literal(min(l, r), type)
        self.IT = value
        return value

    def evaluate_comparison(self, ops, n):
        if n.operand == T.EQUAL:
            value = Literal(ops[0].value == ops[1].value, T.TROOF_TYPE)
        if n.operand == T.NOT_EQUAL:
            value = Literal(ops[0].value != ops[1].value, T.TROOF_TYPE)
        self.IT = value
        return value

    def evaluate_concat(self, ops, n):
        if n.operand == T.CONCAT:
            value = Literal("", T.YARN_LIT)
            for op in ops:
                value = Literal(str(value.value) + str(op.value), T.YARN_LIT)
        self.IT = value
        return value
    
    def evaluate_many(self, ops, n):
        if n.operand == T.ANY:
            value = Literal(any(bool(op.value) for op in ops), T.TROOF_TYPE)
        if n.operand == T.ALL:
            value = Literal(all(bool(op.value) for op in ops), T.TROOF_TYPE)
        self.IT = value
        return value


    def evaluate_operation(self, operands, n):

        if n.operand in [T.AND, T.OR, T.NOT, T.ONE]:
            return self.evaluate_boolean(operands, n)

        if n.operand in [T.EQUAL, T.NOT_EQUAL]:
            return self.evaluate_comparison(operands, n)

        if n.operand in [T.ADD, T.SUB, T.MUL, T.DIV, T.MOD, T.MAX, T.MIN]:
            return self.evaluate_arithmetic(operands, n)

        if n.operand in [T.CONCAT]:
            return self.evaluate_concat(operands, n)

        if n.operand in [T.ANY, T.ALL]:
            return self.evaluate_many(operands, n)



    def exec_Ops(self, n):
        args = n.args

        operands = []

        for arg in args:
            if isinstance(arg, Operation):
                operands.append(self.exec_Ops(arg))
            elif isinstance(arg, Identifier):
                if self.functions.get(arg.name):
                    raise RuntimeError(f"Line: Variable {arg} is a function")
                elif arg.name not in self.variables:
                    raise RuntimeError(f"Variable {arg.name} is not defined")
                else:
                    operands.append(self.variables[arg.name])
            else:
                operands.append(arg)


        return self.evaluate_operation(operands, n)

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

        if isinstance(expression, Operation):
            self.exec_Ops(expression)
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
            int(1 if value.value == "WIN" else 0 if value.value == "FAIL" else value.value)
            if target_type == T.NUMBR_TYPE
            else float(1 if value.value == "WIN" else 0 if value.value == "FAIL" else value.value)
            if target_type == T.NUMBAR_TYPE
            else str(value.value)
            if target_type == T.YARN_TYPE
            else bool(value.value) == True
            if target_type == T.TROOF_TYPE
            else value.value
        )
        
        return Literal(converted, target_type)

    def printintg(self, val1):
        if val1 in [True, False]:
            print(f"WIN" if val1 else "FAIL", end='')
        else:
            print(f"NOOB" if val1 is None else val1, end='')
