#!/usr/bin/env python

import Image, ImageDraw, ImageFont
import pickle
import sys

class GridMaker(object):
    def __init__(self, num_rows, num_columns, square_length=10):
        self.num_rows = num_rows
        self.num_columns = num_columns
        self.square_length = square_length
        self.im = Image.new('RGB', 
                            (num_columns * square_length, 
                             num_rows * square_length))
        self.draw = ImageDraw.Draw(self.im)

    def output(self,filename):
        with open(filename, 'w') as f:
            self.im.save(f, 'PNG')

    def _draw_square(self, x, y):
        """Draw a white square with the upper left corner at (x, y)."""
        points = [(x, y), (x + self.square_length, y + self.square_length)]
        self.draw.rectangle(points, fill=(255, 250, 250), outline=(100,100,100))

    #TODO: Make id_ size proportional to square size
    def _draw_id(self, x, y, id_):
        font = ImageFont.truetype("font.ttf", 15)
        self.draw.text((x + 2, y + 2), str(id_), font=font,  fill=(0, 0, 0))

    #TODO Make letter size proportional to square size
    def _draw_letter(self, x, y, letter):
        default_font = ImageFont.load_default()
        font = ImageFont.truetype("font.ttf", 40)
        self.draw.text((x + 10, y + 10), letter.upper(), font=font, fill=(0, 0, 0))

    def draw_square(self, row, column, id_=None, letter=None):
        x = column * self.square_length
        y = row * self.square_length
        self._draw_square(x, y)
        if id_ is not None:
            self._draw_id(x, y, id_)

        if letter is not None:
            self._draw_letter(x, y, letter)

    def draw_outline(self):
        x = self.num_rows * self.square_length - 1
        y = self.num_columns * self.square_length - 1
        self.draw.rectangle([(0, 0), (x, y)], outline=(0, 0, 0))

def main():
    """Pass in a pickled Puzzle to print it."""
    with open(sys.argv[1], 'r') as f:
        puzzle = pickle.load(f)
    rows = puzzle.grid.num_rows
    columns = puzzle.grid.num_columns
    gridmaker = GridMaker(rows, columns, 50)
    for m in range(rows):
        for n in range(columns):
            sq = puzzle.grid[m, n]
            if sq.blacked_out is False:
                gridmaker.draw_square(sq.m, sq.n, sq.id_, sq.letter)
    gridmaker.draw_outline()
    gridmaker.output('pic.png')


if __name__ == '__main__':
    main()
