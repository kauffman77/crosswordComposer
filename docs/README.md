                     _____________________________

                      CROSSWORD PUZZLE GENERATION

                          Christopher Kauffman
                     _____________________________


- Kevin has an interesting problem: crossword puzzle generation
- For his problem he has some interesting variants
- The first is constraint is that he has a fixed set of words he would
  like to appear in the puzzle
- This could be treated at some level as a constraint
  satisfaction/propagation problem however he has a few other criteria
- There should be a fixed fraction of black squares in the puzzle
- Ideally there will be 180-degree symmetry: rotating the puzzle around
  will cause the pattern of white/black to be the same
- He would like it to be as compact as possible, ideally square
- Each of these are constraints except the last which is a sort of
  objective though it might possible by gradually enlarging constraints
  to get it (grow the grid outward)


Another thought occurred to me though which is to consider the problem
first from the satisfaction side

Consider a list of pairs which describe the letters shared in common
with each of the words.

Example:

WORDS: 123456
1. cat
2. deaf
3. dog
4. cringe
5. trifle 123456

LETTER OVERLAP PAIRS / VERTICES A. (1.1,4.1) c in cat/cringe
B. (1.2,2.3) a in cat/deaf C. (1.3,5.1) t in cat/trifle D. (2.1,3.1) d
in deaf/dog E. (2.2,4.6) e in deaf/cringe F. (2.2,5.6) e in deaf/trifle
G. (2.4,5.4) f in deaf/trifle H. (3.3,4.5) g in dog/cringe I. (4.2,5.2)
r in cringe/trifle J. (4.3,5.3) i in cringe/trifle K. (4.6,5.6) e in
cringe/trifle

Form a graph in which each pair is a vertex and edges are drawn between
vertices when they indicate that there is a conflict. Conflicts exist
due to letter overlap or or due to only one of several letters
overlapping between two rords.

For example there should be an edge between

E. (2.2,4.6) e in deaf/cringe
F. (2.2,5.6) e in deaf/trifle

as they both involve the e in deaf. Due to the nature of crosswords, one
must pick the overlap of one or the other. Similarly the overlaps

E) (2.2,4.6) e in deaf/cringe
K) (4.6,5.6) e in cringe/trifle

are connected and cannot coexist in a 2D puzzle as only one of deaf or
trifle could overlap the e in cringe.

This set forms a clique

E. (2.2,4.6) e in deaf/cringe
F. (2.2,5.6) e in deaf/trifle
K. (4.6,5.6) e in cringe/trifle

from which only one vertex could exist in an actual puzzle.

Words can only overlap on one letter so the three vertices

I. (4.2,5.2) r in cringe/trifle
J. (4.3,5.3) i in cringe/trifle
K. (4.6,5.6) e in cringe/trifle

are all connected and only one could appear in an actual
puzzle. Similarly the vertices

F. (2.2,5.6) e in deaf/trifle
G. (2.4,5.4) f in deaf/trifle

are connected as both involve overlap of deaf and trifle.

Once the graph is established any independent set selected from it
represents a set of overlaps which is at least consistent with the
overlaps available in the words.  A maximum independent set
automatically maximizes the crossings and might lead to "better"
crossings in puzzles.

Just selecting an independent set does not guarantee that it is possible
to actually find a 2D grid configuration that realizes the crossings.
However, it creates a set of much stronger constraints which can be
exploited to severely limit the search space.  For example, one can
quickly check an independent set for horizontal/vertical consistency
with simple breadth-first procedure.

Procedure CHECK_HV_CONSISTENCY(words,overlap_pairs): INPUT: list of
words and list of independent set of overlap pairs OUTPUT: list of
assignments of each word as either vertical or horizontal or failure
that the overlap pairs are inconsistent
1. Pick one word W as horizontal (vertical also possible but due to
   symmetry it doesn't matter)
2. Assign W to be horizontal
3. All words that intersect with W are therefore vertical
4. Visit each neighbor of assigned words and assign it to be the
   opposite of its intersecting word
5. If attempting to assign a word a direction when it already has one,
   the independent set must be inconsistent so return failure
6. When all words are visited, terminate and return the list of
   assignments

If an independent set of overlap is found to be HV consistent, then one
can attempt to lay it out in 2D in a straightforward fashion.

Procedure LAYOUT_WORDS(words,word_orientation,overlap_pairs): INPUT:
list of words list of word horizontal/vertical orientations, list of
independent set of overlap pairs OUTPUT: list of coordinates of each
character in each word or failure if the overlap pairs are inconsistent

1. Pick word W from the word list and remove it from the list. Assign it
   random coordinates according to its orientation. Track this in a hash
   table so that a lookup of 'c in cat' gives the coordinates (5,2).
   Possibly also have an inverse table of (5,2)->'c in cat/cringe'
2. For each pair P in the overlap_pairs list which involves W, assign
   the overlapping word V coordinates based on those that exist in the
   table.  Add overlapping words for each V into a queue of
   words. Remove each V from the word list.
3. Pick up another word W from the queue; if it has already been
   assigned coordinates, skip it
4. If W has not been assigned coordinates, locate an overlap with an
   existing word and attempt to add it based on the overlap
5. Check for collisions with existing words while adding coordinates. If
   one results, the independent set is inconsistent and indicate failure
6. Repeat to 3 until the queue of words to place is empty.
7. If the queue of words to place empties but the words list is not
   empty, then the independent set of overlaps has two components; pick
   another word from the list and assign it more coordinates in an
   independent grid repeating from 1.
8. Terminate when the words list is empty.

If the above procedure terminates with success, it produces a valid
layout of the given words but it may include adjacent words which create
nonsense. Example in which the nonsense word "tf" appears.
,----
|     d
|  t  od
| cringe
| ai   a
| tf   f
|  l 
|  e
`----
This can be checked by running a final check on the puzzle to guarantee
that no such nonsense words appear.  Some of these might be repaired by
searching the dictionary for matching words with regexs: platform and
portfolio both work but conflict on the right, artful and outfit both
work.

After finding a valid layout of the desired words, there remains the
task of creating a board that is symmetric and also has the proper
amount of black space on it.  This can be done by selecting some spaces
add words to from a dictionary which can be selected simply via regular
expression search in a dictinoary with sensitivity to the horizontal and
vertical words that are induced. Some recursive search may be required
even at this stage. The important part is to determine what pattern of
black space will be 180-degrees symmetric.

This approach requires a procedure to enumerate all independent sets of
a graph of the character overlaps, ideally in order from maximal to
minimal. Generating all maximal independent sets is NP-complete
apparently but can be done. Each independent set would I presume be a
subset of some maximal independent set..

There are corner cases such as when the LAYOUT_WORDS procedure produces
several independent grids of words which must be stitched together.
This may happen frequently or rarely, no intuition yet.

The feasibility of an independent set can be checked by setting the words as
nodes, with edges between the original pairs of words and determining if the
graph has a valid two coloring.
