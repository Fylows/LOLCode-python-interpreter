import re
from lexer.tokens import *

"""
lexer function 
in: input_string: str
out: list of tokens
"""

def test():
    print("Lexer test")

def lexer(input_string: str) -> list[Token]:
    tokens = []
    i, line = 0, 1
    str_len = len(input_string)
    
    while i < str_len:
        char = input_string[i]
        
        # skip whitespace
        if char in ' \t\r':
            i += 1
            
    
        # Check for newline/semicolon
        elif char == '\n' or char == ';':
            tokens.append(Token(T.NEWLINE, char, line))
            if char == '\n':
                line += 1
            i += 1
            continue
        
        # String literal
        elif char == '"':
            end = input_string.find('"', i + 1)
            if end == -1:
                raise SyntaxError(f"Line {line}: unterminated string")
            tokens.append(Token(T.YARN, input_string[i + 1:end], line))
            i = end + 1
        
        # Check for keywords
        else:
            # 6. keywords
            for keyword, token_type in KEYWORDS:
                if input_string.startswith(keyword, i):
                    end = i + len(keyword)
                    # must end at a word boundary (so HAIR isn't HAI + R)
                    if (keyword[-1].isalnum() and 
                        end < str_len and 
                        (input_string[end].isalnum() or 
                         input_string[end] == "_")):
                        continue
                    tokens.append(Token(token_type, keyword, line))
                    i = end
                    break
            else:
                # 7. identifier
                m = re.match(r"[A-Za-z][A-Za-z0-9_]*", input_string[i:])
                if m:
                    tokens.append(Token(T.IDENT, m[0], line))
                    i += len(m[0])
                #nothing matched: error, never skip silently
                else:
                    raise SyntaxError(f"Line {line}: unexpected character {char!r}")
    # Indicate end of file
    tokens.append(Token(T.EOF, None, line))
    return tokens
