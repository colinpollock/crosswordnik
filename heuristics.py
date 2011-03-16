#!/usr/bin/env python

from __future__ import division

"""
Run tests on board creation decisions to see which choices make the best board.

Decision tree?

Scoring (of constructed board):
  Number of letters placed.
  Number of words placed.

Features (of words to be placed during board construction):
  Number of words span intersects.
  "Scrabble score" of the word.
  Word's length.
  Number of empty squares the span touches.
  Number of filled squares the span touches.

"""

def get_proportion_filled(puzzle):
    """Calculate the proportion of the squares that have letters.
    
    I read that traditionally no more than 16% of the grid should be empty.
    """
    total_squares = puzzle.grid.num_rows * puzzle.grid.num_columns
    num_filled = sum(1 for sq in puzzle.grid if sq.letter is not None)
    return num_filled / total_squares

def get_num_words_placed(puzzle):
    """Return the number of words placed in the puzzle."""
    return len(puzzle.clues)

