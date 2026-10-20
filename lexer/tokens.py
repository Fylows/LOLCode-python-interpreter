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

    # variable declarations
    WAZZUP = auto()
    BUHBYE = auto()
    VAR_DECLARE = auto()
    VAR_TYPE = auto()
    VAR_ASSIGN = auto()

    # operations

    # arithmetic
    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    MOD = auto()

    # minmax
    MIN = auto()
    MAX = auto()

    # equality
    AND = auto()
    OR = auto()
    ONE = auto()
    NOT = auto()
    ANY = auto()
    ALL = auto()
    EQUAL = auto()
    NOT_EQUAL = auto()

    # concat
    CONCAT = auto()

    # typecast
    TYPECAST = auto()
    A = auto()
    REASSIGN = auto()

    # delimiter
    MKAY = auto()

# ALL KEYWORDS OF OUR LANGUAGE
KEYWORDS = [
    ("HAI", T.HAI),
    ("KTHXBYE", T.KTHXBYE),

    ("WAZZUP", T.WAZZUP),
    ("BUHBYE", T.BUHBYE),

    ("I HAS A", T.VAR_DECLARE),
    ("ITZ", T.VAR_TYPE),
    ("R", T.VAR_ASSIGN),

    ("SUM OF", T.ADD),
    ("DIFF OF", T.SUB),
    ("PRODUKT OF", T.MUL),
    ("QUOSHUNT OF", T.DIV),
    ("MOD OF", T.MOD),
    ("BIGGR OF", T.MAX),
    ("SMALLR OF", T.MIN),

    ("BOTH OF", T.AND),
    ("EITHER OF", T.OR),
    ("WON OF", T.ONE),
    ("NOT", T.NOT),
    ("ANY OF", T.ANY),
    ("ALL OF", T.ALL),
    ("BOTH SAEM", T.EQUAL),
    ("DIFFRINT", T.NOT_EQUAL),

    ("SMOOSH", T.CONCAT),

    ("MAEK", T.TYPECAST),
    ("A", T.A),
    ("IS NOW A", T.REASSIGN),

    ("MKAY", T.MKAY),

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