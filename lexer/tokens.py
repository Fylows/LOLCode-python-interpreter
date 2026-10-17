from dataclasses import dataclass
from enum import Enum,auto

# Make a type for class
class T(Enum):
    #EOF
    EOF = auto()
    
    # Newline
    NEWLINE = auto()
    
    # program start and end
    HAI = auto()
    KTHXBYE = auto()
    
    # printing
    VISIBLE = auto()
    
    # literals
    IDENT = auto()
    NUMBAR = auto()
    NUMBR = auto()
    YARN = auto()
    

# ALL KEYWORDS OF OUR LANGUAGE
KEYWORDS = [
    ("HAI", T.HAI),
    ("KTHXBYE", T.KTHXBYE),
    ("VISIBLE", T.VISIBLE)
]
 
"""
TOKEN is a 
type, which is an enum that represents what kind it is
value, string we're representing the type of
line, what line it is on
"""
@dataclass
class Token:
    type: T
    value: str
    line: int