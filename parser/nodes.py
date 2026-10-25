from dataclasses import dataclass
from lexer.tokens import T

class Node: pass

"""
EACH AST NODE IS A CLASS THAT INHERITS FROM NODE
"""
@dataclass
class Program(Node):
    body: list

@dataclass
class Print(Node):
    args: list
    
@dataclass
class Literal(Node):
    value: any
    type: any = None

@dataclass
class Var(Node):
    name: str
    value: any
    type: any = None

@dataclass
class Function(Node):
    body: list
    args: list = None

@dataclass
class FunctionCall(Node):
    name: str
    argv: list
    argc: int

@dataclass 
class Identifier(Node):
    name: str
    type: any = None

@dataclass
class MyReturn(Node):
    value: any
    type: any = None

@dataclass
# name of var and what to reasign it to
class Typecast(Node):
    value: any
    type: any = None

@dataclass
# what value to reassign
class Reassign(Node):
    name: str
    value: any = None
    type: any = None