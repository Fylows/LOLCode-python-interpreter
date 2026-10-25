HAI
    BTW ---- variable declaration ----
    I HAS A name ITZ "Yel"
    I HAS A age ITZ 20
    I HAS A pi ITZ 3.14
    I HAS A blank
    VISIBLE name
    VISIBLE age
    VISIBLE pi

    BTW ---- reassignment ----
    age R 21
    name R "Bob"
    blank R 5
    VISIBLE age
    VISIBLE name
    VISIBLE blank
    name R age
    VISIBLE name

    BTW ---- typecasting (in place) ----
    I HAS A n ITZ 42
    n IS NOW A YARN
    VISIBLE n
    n IS NOW A NUMBAR
    VISIBLE n

    BTW ---- typecasting (as an expression) ----
    VISIBLE MAEK 3.99 A NUMBR
    VISIBLE MAEK "7" A NUMBR
    VISIBLE MAEK 0 A TROOF
    VISIBLE MAEK 1 A TROOF

    BTW ---- function definitions ----
    HOW IZ I greet
        VISIBLE "hello"
    IF U SAY SO

    HOW IZ I echo YR x
        FOUND YR x
    IF U SAY SO

    HOW IZ I pair YR a AN YR b
        VISIBLE a
        FOUND YR b
    IF U SAY SO

    HOW IZ I stop
        VISIBLE "before"
        GTFO
        VISIBLE "never printed"
    IF U SAY SO

    BTW ---- function calls ----
    I IZ greet MKAY
    VISIBLE I IZ echo YR "hi" MKAY
    VISIBLE I IZ pair YR name AN YR 3 MKAY
    I HAS A result ITZ I IZ echo YR 99 MKAY
    VISIBLE result
    result R I IZ echo YR "again" MKAY
    VISIBLE result
    I IZ stop MKAY
KTHXBYE