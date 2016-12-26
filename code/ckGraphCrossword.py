import networkx as nx
import matplotlib.pyplot as plt
import numpy.random
import random
import sys
import itertools
import logging as log

numpy.random.seed(123456789)
random.seed(123456789)

# log.basicConfig(level=log.INFO)

def letterOverlaps(wordA, wordB):
    overlaps = []
    for i in range(len(wordA)):
        for j in range(len(wordB)):
            if wordA[i] == wordB[j]:
                overlaps.append((wordA, i, wordB, j))
    return(overlaps)

def wordListLetterOverlaps(wordList):
    allOverlaps = []
    for i in range(len(wordList)-1):
        for j in range(i+1, len(wordList)):
            for overlap in letterOverlaps(wordList[i], wordList[j]):
                allOverlaps.append(overlap)
    return(allOverlaps)    

def pairFirstWord(overlapPair):
    return overlapPair[0]

def pairFirstWordLetterIndex(overlapPair):
    return overlapPair[1]

def pairFirstWordWordIndex(overlapPair):
    return (pairFirstWord(overlapPair), pairFirstWordLetterIndex(overlapPair))

def pairSecondWord(overlapPair):
    return overlapPair[2]

def pairSecondWordLetterIndex(overlapPair):
    return overlapPair[3]

def pairSecondWordWordIndex(overlapPair):
    return (pairSecondWord(overlapPair), pairSecondWordLetterIndex(overlapPair))

def generateGraph(overlaps):
    G = nx.Graph()
    G.add_nodes_from(overlaps)
    for i in range(len(overlaps)-1):
        for j in range(i+1, len(overlaps)):
            pairA = overlaps[i]
            pairB = overlaps[j]
            # Add edges for conflicts using the same letter from the same
            # word in more than one crossing
            if pairFirstWordWordIndex(pairA) == pairFirstWordWordIndex(pairB) or \
                pairFirstWordWordIndex(pairA) == pairSecondWordWordIndex(pairB) or \
                pairSecondWordWordIndex(pairA) == pairFirstWordWordIndex(pairB) or \
                pairSecondWordWordIndex(pairA) == pairSecondWordWordIndex(pairB):
                G.add_edge(pairA, pairB)
            # Add edges for conflicts for crossing a pair of words more than once
            if (pairFirstWord(pairA) == pairFirstWord(pairB) and pairSecondWord(pairA) == pairSecondWord(pairB)) or \
                (pairFirstWord(pairA) == pairSecondWord(pairB) and pairSecondWord(pairA) == pairFirstWord(pairB)):
                G.add_edge(pairA, pairB)
    return(G)

# layout is a pair of maps which are
#   "coords" : (i,j) -> [('A',word1,index1,orient1),('A',word2,index2,orient2)]
#   'words'  : word -> (upper left i,j, orientation)

def make_layout():
    return {"words":{}, "coords":{}}

def contains_word(layout,word):
    """Return true if the given word has already been placed in the layout"""
    return word in layout["words"]


def get_word_coordinates_orientation(layout,word):
    """Return the (i,j,orientation) for the given word. i,j are for the
    upper left character in the word. Throw an exception if word is
    not present.

    """
    return layout["words"][word]

def is_word_at_coordinates(layout,i,j):
    """Return True if there is a word with a character at the give coordinates""" 
    return (i,j) in layout["coords"]

def shift_to_origin(layout):
    """Shift the layout so that the min row/col is (0,0)"""
    # Could make this a little more efficient with a single pass
    # through the upper left coords of each word
    mini = min( i for (i,j) in layout["coords"].keys() ) 
    minj = min( j for (i,j) in layout["coords"].keys() )
    shifted = {}
    for (i,j), val in layout["coords"].items():
        shifted[(i-mini,j-minj)] = val
    layout["coords"] = shifted
    
    shifted = {}
    for word,(i,j,orient) in layout["words"].items():
        shifted[word] = (i-mini,j-minj,orient)
    layout["words"] = shifted
    
def twoD_string(layout):
    """Produce a 2D string for given layout. Calls shift_to_origin on the
    layout

    """
    shift_to_origin(layout)
    maxi = max( i for (i,j) in layout["coords"].keys() ) 
    maxj = max( j for (i,j) in layout["coords"].keys() )

    strings = []
    for i in range(maxi+1):
        for j in range(maxj+1):
            if (i,j) in layout["coords"]:
                strings.append(layout["coords"][(i,j)][0][0])
            else:
                strings.append("-")
        strings.append("\n")
    layout_string = "".join(strings)
    return layout_string
                
    

def place_word_in_layout(layout,w_i,w_j,word,orientation, exclude_boundary=False):
    """Place the word in the given layout with specified oritentation with
    coordinates i,j for its upper corner. Modify layout to reflect
    this. Return True on successful placement.  If the word cannot be
    placed due to conflicts with existing words, return False.  Throw
    an exception if this word is already in the layout

    """
    # Check whether new_word has already been placed somewhere else
    if contains_word(layout,word):
        (cur_i,cur_j,cur_o) = get_word_coordinates_orientation(layout,new_word)
        if cur_i==new_i and cur_j==new_j:
            return True         # Already present
        else:
            log.info("Attempting to place at (%d,%d) when already at (%d,%d)"\
                     %(new_i,new_j,cur_i,cur_j))
            return False # Attempting to place new word in two places

    coords = []
    boundary = []
    if orientation=="horizontal":
        coords = list(zip([w_i]*len(word),range(w_j,w_j+len(word))))
        ends = [(coords[0][0],coords[0][1]-1), (coords[-1][0],coords[-1][1]+1)]
    elif orientation=="vertical":
        coords = list(zip(range(w_i,w_i+len(word)),[w_j]*len(word)))
        ends = [(coords[0][0]-1,coords[0][1]), (coords[-1][0]+1,coords[-1][1])]
    else:
        raise Exception("'%s' is not a valid orientation for word '%s'"%(orientation,word))

    # Check ends for freeness
    if exclude_boundary:
        for coord in ends:
            words_at_coord = layout["coords"].get(coord,  []) # default to empty list
            if len(words_at_coord) > 0:
                (e_char,e_word,e_index,e_orient) = words_at_coord[0]
                (e_i,e_j,_) = layout["words"][e_word]
                log.info("(%s,%d,%d) conflicts with (%s,%d,%d) at position (%d,%d)"\
                         %(word,w_i,w_j,e_word,e_i,e_j,coord[0],coord[1]))
                return False
            

    # Place Word
    for index in range(len(word)):
        coord = coords[index]
        char = word[index]
        log.debug("coord: %s char: %s"%(coord,char))
        words_at_coord = layout["coords"].get(coord,  []) # default to empty list

        if len(words_at_coord) > 1: # Check for too many words at a position already
            log.info("multiple words '%s' already at (%d,%d), cannot place '%s' at (%d,%d)"\
                     %(existing_words,coord[0],coord[1],word,w_i,w_j))
            return False
        elif len(words_at_coord) == 1: # Check existing word overlap at that position matches
            (e_char,e_word,e_index,e_orient) = words_at_coord[0]
            if char != e_char:
                (e_i,e_j,_) = layout["words"][e_word]
                log.info("(%s,%d,%d) conflicts with (%s,%d,%d) at position (%d,%d)"\
                         %(word,w_i,w_j,e_word,e_i,e_j,coord[0],coord[1]))
                return False
        elif exclude_boundary:  # No crossing word, check boundary if requested
            boundary_coords = []
            if orientation=="horizontal":
                boundary_coords = [(coord[0]-1,coord[1]), (coord[0]+1,coord[1])]
            elif orientation=="vertical":
                boundary_coords = [(coord[0],coord[1]-1), (coord[0],coord[1]+1)]
            else:
                raise Exception("'%s' is not a valid orientation for word '%s'"%(orientation,word))
            for bcoord in boundary_coords:
                words_at_bcoord = layout["coords"].get(bcoord,  []) # default to empty list
                if len(words_at_bcoord) > 0:                        # existing word around boundary
                    (e_char,e_word,e_index,e_orient) = words_at_bcoord[0]
                    # print(word)
                    (e_i,e_j,_) = layout["words"][e_word]
                    log.info("(%s,%d,%d) conflicts with (%s,%d,%d) at boundary position (%d,%d)"\
                             %(word,w_i,w_j,e_word,e_i,e_j,bcoord[0],bcoord[1]))
                    return False
                
        # Passed all checks, add char at coord
        words_at_coord.append((char,word,index,orientation)) # Append word to list at that position
        layout["coords"][coord] = words_at_coord             # Re-insert list in case it was fresh
    

    # existing_words = layout["coords"][coord]

    # Successfully added all chars of word, now in layout
    layout["words"][word] = (w_i,w_j,orientation)
    return True
                    

def construct_layout(word_list,list_of_crossings):
    """Construct a layout for the given list of character crossings. Return
    the layout if feasibl. Return None if not possible. 

    """
    try:
        # print("CROSSINGS: "+str(list_of_crossings))

        word_crossing_graph = nx.Graph()
        word_crossing_graph.add_nodes_from(word_list)

        for pair in list_of_crossings:
            word_crossing_graph.add_edge(pairFirstWord(pair), pairSecondWord(pair))

        # Can't handle disconnected components right now so bail on this
        if not (nx.is_connected(word_crossing_graph)):
            log.info("Word crossings not connected; layout failed")
            return None

        # Try horizontal/vertical feasibility; construct a graph and
        # then attempt a two-coloring
        colors = nx.algorithms.bipartite.color(word_crossing_graph)
        col2hv = lambda v: (["horizontal","vertical"])[v]
        orientations = {k: col2hv(v) for k,v in colors.items()}
        log.info("Horizontal/Vertical feasible layout found")

        # Now know that horiz/vert is feasible, try to construct a 2D
        # layout by visiting each node in the word_crossing_graph in a
        # breadth first fashion. 2D coorindates are arbitrary
        # pos/negative. Transpose layout after placement so that the
        # upper left is at (0,0).
        layout = make_layout()

        # Place to the first word, subsequent words are the second in
        # the pair of breadth first edges.
        first_word = word_list[0]
        place_word_in_layout(layout,0,0,first_word,orientations[first_word],exclude_boundary=False)
        
        # Need to look up crossing indices during placement to
        # determine starting positions of new words.
        word_crossing_index_dict = {}
        for pair in list_of_crossings:
            ((wA,iA),(wB,iB)) = (pairFirstWordWordIndex(pair),pairSecondWordWordIndex(pair))
            word_crossing_index_dict[(wA,wB)] = (iA,iB)
            word_crossing_index_dict[(wB,wA)] = (iB,iA)
        

        log.info("Beginning breadth first traversal to place reached words")
        for (prev_word,next_word) in nx.bfs_edges(word_crossing_graph, first_word):
            log.debug("layout['coords'] = %s\nlayout['words'] = %s"%(layout["coords"],layout["words"]))
            
            # Determine upper left i,j coordinates of the new_word
            # based on intersection of prev_word.
            (prev_index,next_index) = word_crossing_index_dict[(prev_word,next_word)]
            (prev_i,prev_j,prev_o) = get_word_coordinates_orientation(layout,prev_word)
            (next_i,next_j,next_o) = (None,None,orientations[next_word])
            if prev_o == "horizontal" and next_o == "vertical":
                log.debug("prev_i: %s prev_j: %s prev_index: %s"%(prev_i,prev_j,prev_index))
                (cros_i,cros_j) = (prev_i,prev_j+prev_index)
                (next_i,next_j) = (cros_i-next_index,cros_j)
            elif prev_o == "vertical" and next_o == "horizontal":
                log.debug("prev_i: %s prev_j: %s prev_index: %s"%(prev_i,prev_j,prev_index))
                (cros_i,cros_j) = (prev_i+prev_index,prev_j)
                (next_i,next_j) = (cros_i,cros_j-next_index)
            else:
                raise Exception("Invalid orientation pairs: prev_word: '%s' as '%s', next_word: '%s' as '%s'"\
                                % (prev_word,prev_o,next_word,next_o))
            
            success = place_word_in_layout(layout,next_i,next_j,next_word,next_o,exclude_boundary=False)
            if success:
                log.info("Placed '%s'"%next_word)
            else:
                log.info("Failed at '%s'"%next_word)
                return None
            
        # Placed all words return layout
        return layout

    except nx.NetworkXError:
        log.info("Horizontal/Vertical infeasible backtracking")
        return None

def ck_maximal_independent_set(G, nodes=None):
    """Modification of nx.maximal_independent_set(G) to induce
    deterministic behavior. Inefficient right now due to to need to
    sort whenever a set elemtn is extracted.

    """

    if not nodes:
        nodes = set([sorted(list(G.nodes()))[0]]) # sorting required for determinism
    else:
        nodes = set(nodes)
    if not nodes.issubset(G):
        raise nx.NetworkXUnfeasible("%s is not a subset of the nodes of G" % nodes)
    neighbors = set.union(*[set(G.neighbors(v)) for v in nodes])
    if set.intersection(neighbors, nodes):
        raise nx.NetworkXUnfeasible("%s is not an independent set of G" % nodes)
    indep_nodes = list(nodes)
    available_nodes = set(G.nodes()).difference(neighbors.union(nodes))
    while available_nodes:
        node = sorted(list(available_nodes))[0] # sorting required for determinism
        indep_nodes.append(node)
        available_nodes.difference_update(G.neighbors(node) + [node])
    return indep_nodes



if __name__ == '__main__':

    if len(sys.argv) < 2:
        print("usage: python ckGraphCrossword.py word_list.txt")
        sys.exit(1)

    filename = sys.argv[1]
    word_list = []
    with open(filename) as f:
        word_list = f.read().splitlines()
    
    log.info("%d words read from %s" % (len(word_list),filename))

    # Over all pairs of words, call letterOverlaps
    overlaps = wordListLetterOverlaps(word_list)
    log.info("%d overlaps constructed"%(len(overlaps)))
    #print(overlaps)
    G = generateGraph(overlaps)
    log.info("Overlap graph constructed")
    # nx.draw_networkx(G);     plt.show()
    maximal_overlaps = ck_maximal_independent_set(G)
    log.info("%d overlaps in maximal independent"%(len(maximal_overlaps)))
    for i in sorted(maximal_overlaps):
        log.info(i)

    # iterate over all independent sets stemming from a maximal
    # independent set trying to find a feasible set
    feasible_overlaps = None
    layout = None
    for subset_size in range(len(maximal_overlaps),0,-1):                   # Largest to smallest subsets
        for subset in itertools.combinations(maximal_overlaps,subset_size): # All possible subsets of given size
            log.info("Trying subset size %d: %s"%(subset_size,subset))
            layout = construct_layout(word_list,subset)
            if layout != None:
                log.info("%d crossings in feasible layout"%subset_size)
                print("%d crossings in feasible layout"%subset_size)
                feasible_overlaps = subset
                break
        if feasible_overlaps != None:
            break
        
    if feasible_overlaps == None:
        print("No maximal sets could be realized :(")
    else:
        log.info("Feasible with crossings:")
        for o in feasible_overlaps:
            log.info(o)
        log.info("feasible layout: %s"%(layout))
        log.debug("coords: %s"%(sorted(layout["coords"].items())))
        layout_string = twoD_string(layout)
        log.debug("coords: %s"%(sorted(layout["coords"].items())))
        print(layout_string)
        
