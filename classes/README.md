# Capture the angry words (ALL CAPS)

[Try it online](https://regex101.com/r/wTreAo/1)

Please use a character class, not just [A-Z]

Your regex flavor will support one or more of:

|`/[[:word:]]+/`|Standard per definition. Note the class is inside a bracket expression ([])|
|`/\p{Word}+/`|Alternate form (use when your regex engine doesn't like the above)|
|`/\w+/`|same as the rest, but not a posix class|

[Cheat sheet for classes](http://www.petefreitag.com/cheatsheets/regex/character-classes/)

[delete]: # (https://regex101.com/delete/7weaOewcrqVUJ5uYO7jgx6fN)
