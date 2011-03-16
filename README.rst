DESCRIPTION
===========
This program builds crossword puzzles by repeatedly searching Wordnik's corpus 
for words that fit on a grid (i.e. can be placed on the grid in such a way that
they have at least one letter in common with another word on the grid and that
no non-words are created during placement). By default the program uses 
Wordnik's Word of the Day as the first word on the grid.

SETUP 
-----
The module wordnik.py is a copy of the Python Wordnik API file at 
https://github.com/colinpollock/wordnik-python. In order to use the API you'll 
need to have a Wordnik API key.

You can get one at "http://api.wordnik.com/signup/". You can pass your key as
an argument to crosswordnik.CrosswordPuzzle or make_puzzle(), or you can set the
variable WORDNIK_API_KEY in config.py


EXAMPLE
=======
Currently there's no GUI. The text interface doesn't suffice for actual gameplay
since it can't display both a square's ID (e.g. the "3" in "3 Down") and its
letter. However, you can see the output of the program by doing running the 
demo() function in crosswordnik.py, reproduced below.

>>> # Make a 10 X 10 puzzle grid and try to add 10 words to it.
>>> puzzle = make_puzzle(10, 10, 10)
>>> print "The grid:\n", puzzle
>>> print "The puzzle has %d clues:" % len(puzzle.clues)
>>> pprint(puzzle.clues)

which generates something like the following:

The grid:

::

+----------+
|night-bat*|
|e**e**i*r*|
|w**n**o*i*|
|successful|
|p**e**c*m*|
|artfuli*p*|
|p**o**e*h*|
|exurban*at|
|r**t**c*n*|
|silhouette|
+----------+

The puzzle has 10 clues:
    {(1, 'ACROSS'): ('night-bat', 'A large nocturnal moth.'),
    (2, 'DOWN'): ('newspapers',
               'third-person singular simple present indicative form of 
                newspaper.'),
    (3, 'ACROSS'): ('successful',
                 'Having achieved wealth or eminence:  a successful 
                  architect.'),
    (4, 'DOWN'): ('henceforth', 'From this time forth; from now on.'),
    (5, 'ACROSS'): ('silhouette',
                 'To cause to be seen as a silhouette; outline:  Figures were 
                  silhouetted against the setting sun. '),
    (6, 'DOWN'): ('triumphant', 'Archaic   Triumphal.'),
    (7, 'DOWN'): ('bioscience', 'See life science.'),
    (8, 'ACROSS'): ('exurban', 'Of, pertaining to, or residing in an exurb'),
    (9, 'ACROSS'): ('artful',
                 'Skillful in accomplishing a purpose, especially by the use of
                  cunning or craft.'),
    (10, 'ACROSS'): ('at',
                  'To or toward the direction or location of, especially for a 
                   specific purpose:  Questions came at us from all sides. ')}


TODO/IMPROVEMENTS
=================
* Fix the markup for the example run.

* See TODO.rst.
