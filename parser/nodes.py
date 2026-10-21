from dataclasses import dataclass

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

@dataclass
class Var(Node):
    name: str
    value: any = None

# functions are always attatched to a variable
@dataclass
class Function(Node):
    body: list
    args: list = None

@dataclass 
class Identifier(Node):
    name: str