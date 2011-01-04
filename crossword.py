#!/usr/bin/env python

import random
import re

with open('/usr/share/dict/words', 'r') as f:
    words = [w.strip() for w in f.readlines() if re.match(r'^\w+$', w)]


class Grid(object):
    def __init__(self, rows, columns):
        self.rows = rows
        self.columns = columns
        self.grid = [[None] * columns for i in range(rows)]

    def __str__(self):
        s = []
        s.append('+' + '-' * self.columns + '+')
        for row in  self.grid:
            curr = ['|']
            for item in row:
                if item is None: 
                    curr.append(' ')
                else:
                    curr.append(item)
            curr.append('|')
            s.append(''.join(curr))
        s.append('+' + '-' * self.columns + '+')
        return '\n'.join(s)

    def __setitem__(self, coordinates, item):
        m, n = coordinates
        print 'in getitem' + '*' * 100
        self.grid[m][n] = item

    def __getitem__(self, coordinates):
        m, n = coordinates
        return self.grid[m][n]

class Word(object):
    """Representation of a word on in the puzzle."""
    pass

class Puzzle(object):
    def __init__(self, rows, columns, word_count):
        self.grid = Grid(rows, columns)
        self._populate_puzzle(word_count)

    def __str__(self):
        return str(self.grid)

    def _populate_puzzle(self, word_count):
        for i in range(word_count):
            self._place_word()

    def _random_coords(self):
        m = random.randint(0, self.grid.rows - 1)
        n = random.randint(0, self.grid.columns - 1)
        assert self.grid[m, n] is None
        return (m, n)
        
    def _get_word(self, pattern):
        pattern = "^%s$" % pattern
        print "pat is", pattern
        pat = re.compile(pattern, re.MULTILINE)
        m = pat.findall('\n'.join(words))
        assert m # eventually just return None and retry
        return random.choice(m)

    def _place_word(self):
        m, n = self._random_coords()
        #TODO: Find a pattern for a word to be placed and the direction
        pat, direction = self._find_patterns(m, n)
        pat = '..a..'
        direction = 'VERTICAL'
        word = self._get_word(pat)
        for i, char in enumerate(word):
            print "(%d) %s" % (i, char),
            if direction == 'VERTICAL':
                self.grid[m + i, n] = char
            elif direction == 'HORIZONTAL':
                self.grid[m, n + 1] = char


    def _find_patterns(self, m, n):
        """Find the patterns for a new word from self.grid[m, n].
        
        Return a list of tuples that look like:
        (('a', '.', 'k'), 'VERTICAL')
        """
        assert False, 'Start here'

        


def main():
    puzzle = Puzzle(20, 20, 2)
    print puzzle

if __name__ == '__main__':
    main()
