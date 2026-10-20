import re
from lexer.tokens import *

"""
lexer function 
in: input_string: str
out: list of tokens
"""
# https://www.geeksforgeeks.org/python/re-compile-in-python/
# compile for faster performance
numbr = re.compile(r"-?[0-9]+")
numbar = re.compile(r"-?[0-9]+\.[0-9]+")
ident = re.compile(r"[A-Za-z][A-Za-z0-9_]*")

def lexer(input_string: str) -> list[Token]:
    tokens = []
    i, line = 0, 1
    str_len = len(input_string)

    
    while i < str_len:
        char = input_string[i]
        # skip whitespace
        if char in " \t\r":
            i += 1
        
        elif input_string.startswith("BTW", i):
            while i < str_len and input_string[i] != '\n':
                i += 1
            
        elif input_string.startswith("OBTW", i):
            while i < str_len and not input_string.startswith("TLDR", i):
                i += 1
                if i < str_len and input_string[i] == '\n':
                    line += 1
            i += 4  # Skip "TLDR"
        
        # Check for newline/semicolon
        elif char == '\n' or char == ';':
            tokens.append(Token(T.NEWLINE, char, line))
            if char == '\n':
                line += 1
            i += 1
            continue
        
        # literals
        elif char == '"':
            end = input_string.find('"', i + 1)
            if end == -1:
                raise SyntaxError(f"Line {line}: unterminated string")
            tokens.append(Token(T.YARN, input_string[i + 1:end], line))
            i = end + 1
        # float
        elif re.match(numbar, input_string[i:]):
            m = re.match(numbar, input_string[i:])
            tokens.append(Token(T.NUMBAR, m[0], line))
            i += len(m[0])

        # int
        elif re.match(numbr, input_string[i:]):
            m = re.match(numbr, input_string[i:])
            tokens.append(Token(T.NUMBR, m[0], line))
            i += len(m[0])

        # Check for keywords
        else:
            for keyword, token_type in KEYWORDS:
                if input_string.startswith(keyword, i): # at char i, check if keyword matches
                    end = i + len(keyword) # must end at a word boundary 
                    if (end < str_len and 
                        (input_string[end].isalnum() or 
                         input_string[end] == "_")):
                        continue
                    tokens.append(Token(token_type, keyword, line))
                    i = end
                    break
            else:
                # check for identifiers
                m = re.match(ident, input_string[i:])
                if m:
                    tokens.append(Token(T.IDENT, m[0], line))
                    i += len(m[0])
                # nothing matched: error
                else:
                    raise SyntaxError(f"Line {line}: unexpected character {char!r}")
    # Indicate end of file
    tokens.append(Token(T.EOF, None, line))
    return tokens
