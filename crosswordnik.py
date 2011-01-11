#!/usr/bin/env python

"""
This module contains code for creating crossword puzzles using the Wordnik API
to find words and get their definitions to use as clues.

Though it will(?) be possible to create the puzzles manually, at this time you
have to let the program make all the decisions. It begins by placing the Wordnik
Word of the Day in the top left corner of the grid and then adds words from
Wordnik's corpus until no new words fit.

The following example shows basic setup and game play. The text based interface
isn't usable for actual game play so you would also need a way of displaying
the grid and clues to the user and a way to get the user's input.
>>> puzzle = CrosswordPuzzle(10, 10)  # Create a 10 X 10 puzzle grid
>>> puzzle.populate_puzzle()
>>> while not puzzle.is_completed:
>>>     # SHOW GRID AND CLUES TO USER
>>>     m, n, letter = # GET INPUT FROM USER
>>>     puzzle.enter_from_user(m, n, letter)
"""


from pprint import pprint
import random
import sys

from wordnik import Wordnik

import config


class Square(object):
    """Representation for a square on a grid."""

    def __init__(self, m, n):
        self.m = m
        self.n = n
        self._letter = None
        self.user_entry = None
        self.id_ = None
        self._blacked_out = False

    @property
    def letter(self):
        """Return the puzzle letter in the square (not the user's guess)."""
        return self._letter

    @letter.setter
    def letter(self, val):
        """Sets the square's letter to be `val` unless square is blacked out."""
        if self.blacked_out is True:
            #TODO: new Exception
            raise ValueError('Letter cannot be set for a blacked out square.')
        self._letter = val
            
    @property
    def blacked_out(self):
        """Return True if the square does not and will not contain a letter."""
        return self._blacked_out 

    @blacked_out.setter
    def blacked_out(self, val):
        """Blacks out the square if True is passed in. Cannot un-black out."""
        if val is not True:
            raise ValueError("Blacking out of a square cannot be reversed.")
        if self.letter is not None:
            raise ValueError('Cannot black out a square containing a letter.')
        self._blacked_out = val

    def __repr__(self):
        return 'Square@(%d, %d)=%s' % (self.m, self.n, self.letter)

    def __str__(self):
        if self.blacked_out is True:
            return '*'
        elif self.letter is None:
            return ' '
        else:
            return self.letter


class Grid(object):
    """A basic, regtangular `m` by `n` grid.

    Each square within the grid is a Square object, which is somewhat specific
    to crossword puzzles and other word games (e.g. has "letter" field). This
    could be avoided by making Square more generic.

    Example, Usage:
        grid = Grid(5, 10)
        sq = grid[0, 9] 
        sq.letter = 'L'
    """

    def __init__(self, rows, columns):
        self.num_rows = rows
        self.num_columns = columns
        self.grid = [[Square(m, n) for n in range(columns)] 
                                   for m in range(rows)]

        # The spans don't chance so they can be computed in the beginning.
        self.all_spans = self._get_all_spans()

    def __str__(self):
        """Return a text representation of the grid."""
        strings = []
        strings.append('+' + '-' * self.num_columns + '+')
        for row in  self.grid:
            curr = ['|']
            for item in row:
                curr.append(str(item))
            curr.append('|')
            strings.append(''.join(curr))
        strings.append('+' + '-' * self.num_columns + '+')
        return '\n'.join(strings)

    def __setitem__(self, (m, n), item):
        """Replace the default Square at (`m`, `n`) with `item`."""
        self.grid[m][n] = item

    def __getitem__(self, (m, n)):
        """Return the Square at (`m`, `n`)."""
        return self.grid[m][n]

    def __iter__(self):
        """Return an iterator of each square in the grid."""
        for m in range(self.num_rows):
            for n in range(self.num_columns):
                yield self.grid[m][n]

    def are_valid_coordinates(self, m, n):
        """Return True if (m, n) are coordinates for a square in the grid."""
        return 0 <= m < self.num_rows and 0 <= n < self.num_columns

    def blackout_all_open_squares(self):
        """Black out all open square in the grid."""
        for m in range(self.num_rows):
            for n in range(self.num_columns):
                sq = self.grid[m][n]
                if sq.letter is None:
                    sq.blacked_out = True

    def blackout_square(self, m, n):
        """Set `blacked_out` for the square at (`m`, `n`) to True."""
        sq = self.grid[m][n]
        if sq.letter is None:
            self.grid[m][n].blacked_out = True

    @staticmethod
    def get_span_direction(span):
        """Return 'ACROSS' or 'DOWN' depending on the direction of `span`."""
        if span[0][0] == span[1][0]:
            return 'ACROSS'
        elif span[0][1] == span[1][1]:
            return 'DOWN'
        else:
            assert False, 'sanity check'

    def get_adjacent_square_positions(self, sq):
        """Return the (m, n) of squares adjacent to `sq` but not diagonally."""
        fil = lambda sq: 0 <= sq[0] < self.num_rows and \
                         0 <= sq[1] < self.num_columns
        m, n = sq.m, sq.n
        return filter(fil, [(m + 1, n), (m, n + 1), (m - 1, n), (m, n - 1)])

    def num_words_touching(self, sq):
        """Return the number of unique words `sq` is touching."""
        #TODO: exclude words that `sq` is part of?
        return sum(1 for (m, n) in self.get_adjacent_square_positions(sq)
                   if self.grid[m][n].letter is not None)

    def a_letter_is_in_span(self, span):
        """Return True if a square at any (m, n) in span contains a letter."""
        return any(self.grid[m][n].letter is not None for (m, n) in span)

    def span_not_touching_too_many_words(self, span, max_touching):
        """Return True if no square in `span` is touching too many words."""
        return all(self.num_words_touching(self.grid[m][n]) <= max_touching
                   for (m, n) in span if self.grid[m][n].letter is None)

    def span_not_on_blacked_out(self, span):
        """Return True if no (m, n) in `span` is a blacked out square."""
        return all(self.grid[m][n].blacked_out is False for (m, n) in span)

    def span_not_full(self, span):
        """Return True if not all squares in `span` contain letters."""
        return any(self.grid[m][n].letter is None for (m, n) in span)

    def open_spans(self, max_words_touching=1):
        """Return a generator of of open spans, where each span is a tuple

        Each span is a tuple of (m, n) pairs, where either m or n increases.

        A span is open if:
           the length of the span is greater than one,
           at least one square is filled with a letter,
           not all squares within it are filled with letters, 
           no square is blacked out, and
           no square is touching more than `max_words_touching` words.
        """
        return (span for span in self.all_spans if
                len(span) > 1 and
                self.a_letter_is_in_span(span) and
                self.span_not_on_blacked_out(span) and 
                self.span_not_full(span) and
                self.span_not_touching_too_many_words(span, 
                                                      max_words_touching))

    def _get_all_spans(self):
        """Return all possible spans on the grid.
        
        The output is only dependent on the dimensions of the grid so it only
        needs to be called once for each grid.
        """
        long_spans = set()
        for m in range(self.num_rows):
            vert_span = []
            hor_span = []
            for n in range(self.num_columns):
                vert_span.append((m, n))
                hor_span.append((n, m))
            long_spans.add(tuple(vert_span))
            long_spans.add(tuple(hor_span))
    
        subspans = set()
        for span in long_spans:
            for i in range(len(span)):
                for j in range(i + 1, len(span) + 1):
                    subspans.add(span[i:j])
        return subspans


class CrosswordPuzzle(object):
    """A crossword puzzle grid that automatically generates puzzles.

    A `m` by `n` grid is populated with words from Wordnik's corpus. Currently
    the resulting crossword puzzle cannot have parallel, adjacent words like you
    would find in the NY TImes crossword.
    
    The grid itself is accessible through the __getitem__ method of the puzzle,
    which provides access to the individual Squares. Clues are taken from 
    Wordnik (definitions, example usages, synonyms, etc.) and are stored in a
    dictionary from clue positions to words and clues:
        self.clues[1, 'DOWN'] => ('cat', 'A small domestic animal')


    In order to create the puzzle you can use the populate_puzzle method, which
    uses Wordnik's Word of the Day as the first word and then adds the specified
    number of words to the puzzle. 
    """

    def __init__(self, rows, columns):
        """Create a `rows` X `columns` grid and initialize the clues dict."""
        self.grid = Grid(rows, columns)
        self.clues = {}
        self.wordnik = Wordnik(config.WORDNIK_API_KEY)
        self._current_sq_id = 1  # To keep track of Square IDs

    def __str__(self):
        """Return the grid as a string."""
        return str(self.grid)

    def populate_puzzle(self, word_count):
        """Try to `word_count` words/clues. Return the number of words added."""
        words_added = 0
        if not self.clues:
            self.place_first_word()
            word_count -= 1
            words_added += 1

        for i in range(word_count):
            result = self.find_and_add_a_word()
            if result is None:
                s = 'Grid filled up after adding %d words.' % len(self.clues)
                print >> sys.stderr, s
                break
            else:
                words_added += 1

        self.finalize()
        return words_added

    def place_first_word(self):
        """Add the Wordnik Word of the Day as the first word in the puzzle."""
        word = self.wordnik.word_of_the_day()['wordstring']

        #TODO: handle the WOTD being too long
        assert len(word) <= self.grid.num_columns
        span = [(0, n) for n in range(len(word))]
        self.add_word(word, span)
            
    def find_and_add_a_word(self):
        """Find a word in the Wordnik corpus that fits the puzzle and add it.
        
        If the search and addition are successful, return the wordstring. If
        not, return None.
        """
        open_spans = sorted(self.grid.open_spans(), key=len, reverse=True)
        for span in open_spans:
            query = ''.join([str(self.grid[m, n]) for (m, n) in span])
            query = query.replace(' ', '?')
            length = len(query)
            words = self.wordnik.word_search(query, max_length=length, 
                                             min_dictionary_count=1)
            if words:
                word = max(words, key=lambda w: w['count'])
                self.add_word(word['wordstring'], span)
                return word['wordstring']
        return None

    def store_clue(self, word, id_, direction, clue):
        """Store a word in self.clues. Call after putting word on the grid."""
        self.clues[id_, direction] = (word, clue)

    def add_word(self, word, span):
        """Place the word on the grid then add it and its clue to self.clues."""
        self.put_word_on_grid(word, span)
        
        m, n = span[0][0], span[0][1]
        first_square = self.grid[m, n]
        if first_square.id_ is None:
            id_ = self._current_sq_id
            self._current_sq_id += 1
        else:
            id_ = first_square.id_
        definitions = self.wordnik.definitions(word)
        definition = random.choice(definitions)['text']
        direction = self.grid.get_span_direction(span)
        
        self.store_clue(word, id_, direction, definition)

    def put_word_on_grid(self, word, span):
        """Add the nth letter in `word` to the nth position in `span`.  """
        assert len(word) == len(span)
        assert len(span) > 1, "Can't insert word shorter than two letters."
        for i, char in enumerate(word):
            (m, n) = span[i]
            if self.grid[m, n].letter is None:
                self.grid[m, n].letter = char
            else:
                assert self.grid[m, n].letter == char

        # Black out open squares on either end of the word if they exist.
        direction = self.grid.get_span_direction(span)
        if direction == 'ACROSS':
            for (m, n) in ((m, n - 1), (m, n + 1)):
                if self.grid.are_valid_coordinates(m, n):
                    self.grid.blackout_square(m, n)

        elif direction == 'DOWN':
            for (m, n) in ((m - 1, n), (m + 1, n)):
                if self.grid.are_valid_coordinates(m, n):
                    self.grid.blackout_square(m, n)
        else:
            assert False, "Sanity check"

    def finalize(self):
        """Perform cleanup after all the words have been placed."""
        self.grid.blackout_all_open_squares()

    #
    # Gameplay related methods
    #
    @property
    def is_completed(self):
        """Return True if the user's entries match the correct letters."""
        for sq in self.grid:
            if sq.letter != sq.user_entry:
                return False
        return True

    def enter_from_user(self, m, n, letter):
        """Set the value of the square at (`m`, `n`) to `letter`."""
        sq = self.grid[m, n]
        assert not sq.is_blacked_out
        sq.letter = letter


def make_puzzle(rows, columns, num_words):
    """Return a `rows` by `columns` crossword puzzle with `num_words` words."""
    puzzle = CrosswordPuzzle(rows, columns)
    puzzle.populate_puzzle(num_words)
    puzzle.finalize()
    return puzzle

def demo():
    # Make a 10 X 10 puzzle grid and try to add 10 words to it.
    puzzle = make_puzzle(10, 10, 10)
    print "The grid:\n", puzzle
    print "The puzzle has %d clues:" % len(puzzle.clues)
    pprint(puzzle.clues)

if __name__ == '__main__':
    demo()
