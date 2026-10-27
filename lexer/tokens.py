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
    TROOF = auto()
    NOOB = auto()
    WIN = auto()
    FAIL = auto()

    # variable declarations
    WAZZUP = auto()
    BUHBYE = auto()
    VAR_DECLARE = auto()
    VAR_TYPE = auto()
    VAR_ASSIGN = auto()

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

    AN = auto()
    # typecast
    TYPECAST = auto()
    A = auto()
    REASSIGN = auto()

    # delimiter
    MKAY = auto()

    # input
    INPUT = auto()

    # conditionals
    IF = auto()
    THEN = auto()
    ELIF = auto()
    ELSE = auto()
    ENDIF = auto()
    SWITCH = auto()
    CASE = auto()
    DEFAULT = auto()

    # loops
    LOOP_START = auto()
    INC = auto()
    DEC = auto()
    UNTIL = auto()
    WHILE = auto()
    LOOP_END = auto()
    BREAK = auto()

    # functions
    FUNCTION = auto()
    FUNC_START = auto()
    FUNC_END = auto()
    RETURN = auto()
    FUNC_CALL = auto()

    # func and loop connector
    YR = auto() 

    # comments
    BTW = auto()
    OBTW = auto()
    TLDR = auto()

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
    ("BOTH SAEM", T.EQUAL),
    ("DIFFRINT", T.NOT_EQUAL),

    ("ANY OF", T.ANY),
    ("ALL OF", T.ALL),

    ("NUMBR", T.NUMBR), 
    ("NUMBAR", T.NUMBAR),  
    ("YARN", T.YARN),
    ("TROOF", T.TROOF),
    ("WIN", T.WIN),
    ("FAIL", T.FAIL),
    ("NOOB", T.NOOB),
    ("AN", T.AN),


    ("SMOOSH", T.CONCAT),

    ("MAEK", T.TYPECAST),
    ("A", T.A),
    ("IS NOW A", T.REASSIGN),

    ("MKAY", T.MKAY),
    ("VISIBLE", T.VISIBLE),

    ("GIMMEH", T.INPUT),

    ("O RLY?", T.IF),
    ("YA RLY", T.THEN),
    ("MEBBE", T.ELIF),
    ("NO WAI", T.ELSE),
    ("OIC", T.ENDIF),
    ("WTF?", T.SWITCH),
    ("OMG", T.CASE),
    ("OMGWTF", T.DEFAULT),

    ("YR", T.YR),
    
    ("IM IN YR", T.LOOP_START),
    ("UPPIN", T.INC),
    ("NERFIN", T.DEC),
    ("TIL", T.UNTIL),
    ("WILE", T.WHILE),
    ("IM OUTTA YR", T.LOOP_END),
    ("GTFO", T.BREAK),
    
    ("HOW IZ I", T.FUNC_START),
    ("IF U SAY SO", T.FUNC_END),
    ("FOUND YR", T.RETURN),
    ("I IZ", T.FUNC_CALL),

    ("BTW", T.BTW),
    ("OBTW", T.OBTW),
    ("TLDR", T.TLDR)
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