Bugs
====
* Occasionally two parallel words will overlap and create a non-word. For
  example, the two words below have an overlap that the grid creation program
  isn't aware of.

    cat
      dog



Game & Grid Improvements
===========================
* In the puzzle creation, words are only placed on spans of squares if those
  spans aren't adjacent to any other spans. This makes it possible to search
  for new words without having to worry about a lot of constraints. Consider
  the words below.
  
      crow
      a
      t
  
    If the program were allowed to place words next to other words then it would
    be allowed to place "run" vertically starting from the "r" in "crow", like
    this.
  
      crow
      au
      tn
  
    But since "au" and "tn" aren't words (and non-words can't be left on the
    grid) the program would need to add more letters. In the case of "tn" this
    would be hard since few if any words begin with "tn". There are plenty of
    words that begin with "au", but adding letters to the right of "au" will
    create yet another problem. For example, turning "au" into "aunt" solves
    one problem, but then we need words beginning in "on" and "wt".
  
      crow
      aunt
      tn
  
    With enough words this would be possible for a small grid. But with a large
    grid the number of dependencies gets huge. Naively searching and adding
    words that fulfill all constraints until the grid is full isn't practical.

    My cheap approach of spacing out words goes against how crossword puzzles
    are supposed to be, at least the official ones like the NYT's. One possible
    approach that avoids the sparse grid is using some heuristics to direct
    the search. For example, choosing words containing common letters would
    make it easier later to find words that'll fit.

    What I'm hoping to do is partially fill the grid using my cheap method, then
    use expensive methods after a point. Of course it'll still be beneficial to
    use some heuristics during both phases.

* Add difficulty levels by controlling:
    + Word frequency (more frequent words are probably easier to guess).
    + Clue type (example usage with word blanked out vs. definitions.
    + Word length.

* Exclude words that contain punctuation or spaces.

* Make  GUI, either with TKinter or JS/CSS/etc.. The text based interface isn't
  useable since I can't display the clue index in the square and also display
  letters.

Conforming to "Official" Crossword Rules
=======================================-
* Grid layout needs to be symmetrical top-to-bottom.

* Minimize black squares (less than 16% of board?).

* Avoid "unkeyed letters" that do not appear in at least one across and one
  down word.

* The minimum word length should be three letters.

* Use theme words somehow.

* Don't repeat words.

* Use 15 X 15 grid as default.


Ideas
=====
* Do this in Prolog.


