#!/usr/bin/env python

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
