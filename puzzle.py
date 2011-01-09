#!/usr/bin/env python


"""
This module contains code for creating crossword puzzles using the Wordnik API
to find words and get their definitions to use as clues.
"""

from pprint import pprint
import random
import sys

from wordnik import Wordnik


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
        """Blacks out the square if True is passed in."""
        if val is not True:
            raise ValueError("Blacking out of a square cannot be reversed.")
        if self.letter is not None:
            raise ValueError('Cannot black out a square containing a letter.')
        self._blacked_out = val


    def __repr__(self):
        return 'Square@(%d, %d)=%s' % (self.m, self.n, self.letter)
        #TODO: add user entry

    def __str__(self):
        if self.blacked_out is True:
            return '*'
        elif self.letter is None:
            return ' '
        else:
            return self.letter

class _FullGridError(Exception):
    """Raised during puzzle creation when grid is full and insertion fails."""

class Grid(object):
    def __init__(self, rows, columns):
        self.num_rows = rows
        self.num_columns = columns
        self.grid = [[Square(m, n) for n in range(columns)] 
                                   for m in range(rows)]
    def __str__(self):
        s = []
        s.append('+' + '-' * self.num_columns + '+')
        for row in  self.grid:
            curr = ['|']
            for item in row:
                curr.append(str(item))
            curr.append('|')
            s.append(''.join(curr))
        s.append('+' + '-' * self.num_columns + '+')
        return '\n'.join(s)

    def __setitem__(self, (m, n), item):
        self.grid[m][n] = item

    def __getitem__(self, (m, n)):
        return self.grid[m][n]

class Word(object):
    """Representation of a word on in the puzzle."""
    pass

class Puzzle(object):
    def __init__(self, rows, columns, word_count):
        self.grid = Grid(rows, columns)
        #self.words = set()
        self.words = {}

        self._current_id = 1  # To keep track of Square IDs during grid creation
        self._populate_puzzle(word_count)
        self._blackout_blanks()

    def __str__(self):
        return str(self.grid)

    def _populate_puzzle(self, word_count):
        #TODO: move key to config file
        api_key = "08f33bb1a9d567c976c780c692001f689d039041b0b93a0cb"
        self.wordnik = Wordnik(api_key)
        self._place_seed_word()
        for i in range(word_count - 1):
            try:
                self._find_and_add_a_word()
            except _FullGridError:
                s = 'Board filled up after adding %d words.' % len(self.words)
                print >> sys.stderr, s
                break

    def _place_seed_word(self):
        wotd = self.wordnik.word_of_the_day()
        word = wotd['wordstring']
        #TODO: handle the WOTD being too long
        assert len(word) <= self.grid.num_columns
        #TODO: Choose starting position
        span = [(0, n) for n in range(len(word))]
        self._add_word(word, span)
            

    def _find_and_add_a_word(self):
        #TODO: parameterize the span length then weight the choice
        open_spans = sorted(self._open_spans(), key=len, reverse=True)
        for span in open_spans:
            query = ''.join([str(self.grid[m, n]) for (m, n) in span])
            query = query.replace(' ', '?')
            length = len(query)
            words = self.wordnik.word_search(query, max_length=length, 
                                             min_dictionary_count=1)
            if words:
                # Currently choosing most frequent word. Parameterize!
                word = max(words, key=lambda w: w['count'])
                self._add_word(word['wordstring'], span)
                return

        #TODO: fail if no words work. backtrack?
        raise _FullGridError

    def _store_word(self, word, id_, direction, clue):
        """Store a word in self.words. Call after putting word on the grid."""
        self.words[id_, direction] = (word, clue)
        #TODO clues

    @staticmethod
    def _get_span_direction(span):
        #TODO contants
        if span[0][0] == span[1][0]: 
            return 'HORIZONTAL'
        elif span[0][1] == span[1][1]: 
            return 'VERTICAL'
        else:
            assert False, "Sanity check"
        return 'VERTICAL'

    def _add_word(self, word, span):
        """Place the word on the grid then add it and its clue to self.words."""
        self._put_word_on_grid(word, span)
        
        m, n = span[0][0], span[0][1]
        first_square = self.grid[m, n]
        if first_square.id_ is None:
            id_ = self._current_id
            self._current_id += 1
        else:
            id_ = first_square.id_
        definitions = self.wordnik.definitions(word)
        definition = random.choice(definitions)['text']
        direction = self._get_span_direction(span)
        
        self._store_word(word, id_, direction, definition)

    def _blackout_blanks(self):
        for m in range(self.grid.num_rows):
            for n in range(self.grid.num_columns):
                sq = self.grid[m, n]
                if sq.letter is None:
                    sq.blacked_out = True

    # Black out a square based on the given m, n if they're valid coordinaes
    def _blackout_square(self, m, n):
        if 0 <= m < self.grid.num_rows and 0 <= n < self.grid.num_columns:
            sq = self.grid[m, n]
            if sq.letter is None:
                self.grid[m, n].blacked_out = True


    def _put_word_on_grid(self, word, span):
        assert len(span) > 1, "Can't insert word shorter than two letters."
        for i, char in enumerate(word):
            (m, n) = span[i]
            if self.grid[m, n].letter is None:
                self.grid[m, n].letter = char
            else:
                assert self.grid[m, n].letter == char


        # Black out open squares on either end of the word.
        direction = self._get_span_direction(span)
        if direction == 'HORIZONTAL':
            self._blackout_square(m, n - 1)
            self._blackout_square(m, n + 1)
        elif direction == 'VERTICAL':
            self._blackout_square(m, n - 1)
            self._blackout_square(m, n + 1)
        else:
            assert False, "Sanity check"

    def _all_spans(self):
        spans = set()
        for m in range(self.grid.num_rows):
            vert_span = []
            hor_span = []
            for n in range(self.grid.num_columns):
                vert_span.append((m, n))
                hor_span.append((n, m))
            spans.add(tuple(vert_span))
            spans.add(tuple(hor_span))
    
        subspans = set()
        for span in spans:
            for i in range(len(span)):
                for j in range(i + 1, len(span) + 1):
                    subspans.add(span[i:j])

        return subspans

    def _adjacent_square_positions(self, sq):
        fil = lambda sq: 0 <= sq[0] < self.grid.num_rows and \
                         0 <= sq[1] < self.grid.num_columns
        m, n = sq.m, sq.n
        return filter(fil, [(m + 1, n), (m, n + 1), (m - 1, n), (m, n - 1)])


    def _num_words_touching(self, sq):
        # this doesn't work when the square is part of a word
        return sum(1 for (m, n) in self._adjacent_square_positions(sq)
                   if self.grid[m, n].letter is not None)

    def _a_letter_is_in_span(self, span):
        return any(self.grid[m, n].letter is not None for (m, n) in span)

    def _span_not_touching_too_many_words(self, span, max_touching):
        # Return True if no square in the span that is not part of a word is
        # touching more than `max_touching` words.
        return all(self._num_words_touching(self.grid[m, n]) <= max_touching 
                   for (m, n) in span if self.grid[m, n].letter is None)

    def _span_not_on_blacked_out(self, span):
        return all(self.grid[m, n].blacked_out == False for (m, n) in span)

    def _span_not_full(self, span):
        return any(self.grid[m, n].letter is None for (m, n) in span)

    def _open_spans(self, max_words_touching=1):
        # spans longer than 1
        return (span for span in self._all_spans() if
                len(span) > 1 and
                self._span_not_full(span) and
                self._a_letter_is_in_span(span) and
                self._span_not_on_blacked_out(span) and 
                self._span_not_touching_too_many_words(span, 
                                                            max_words_touching))



def main():
    puzzle = Puzzle(10, 10, 10)
    print puzzle
    print len(puzzle.words)
    pprint(puzzle.words)

if __name__ == '__main__':
    main()
