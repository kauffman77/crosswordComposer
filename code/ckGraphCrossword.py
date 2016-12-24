import networkx as nx
import matplotlib.pyplot as plt
import random
import sys
import itertools

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

def construct_layout(word_list,list_of_overlaps):
    """Construct a layout for the given list of character overlaps. Return
    the layout if feasibl. Return None if not possible. 

    """
    try:
        # First try horizontal/vertical feasibility; construct a graph and
        # then attempt a two-coloring
        word_crossing_graph = nx.Graph()
        word_crossing_graph.add_nodes_from(word_list)
        for pair in list_of_overlaps:
            word_crossing_graph.add_edge(pairFirstWord(pair), pairSecondWord(pair))
        colors = nx.algorithms.bipartite.color(word_crossing_graph)
        col2hv = lambda v: (["horizontal","vertical"])[v]
        orientation = {k: col2hv(v) for k,v in colors.items()}
        nx.set_node_attributes(word_crossing_graph,'orientation',orientation)

        # Now know that horiz/vert is feasible, try to construct a 2D
        # layout by visiting each node in the word_crossing_graph in a
        # breadth first fashion
        coordinates_to_letter_word = {}
        word_to_coordinates = {}
        first_word = word_list[0]
        
        print("Beginning breadth first traversal")
        for (wordA,wordB) in nx.bfs_edges(word_crossing_graph, first_word):
            print(wordA +" "+wordB)
            if not(wordA in word_to_coordinates):
                word_to_coordinates[wordA] = "present"
            if not(wordB in word_to_coordinates):
                word_to_coordinates[wordB] = "present"

        print(word_to_coordinates)
        print("Remaining words: " + str(set(word_to_coordinates.keys()).difference(set(word_list))))

        return orientation
    except nx.NetworkXError:
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

    random.seed(123456789)
    filename = sys.argv[1]
    word_list = []
    with open(filename) as f:
        word_list = f.read().splitlines()
    
    print("%d words read from %s" % (len(word_list),filename))

    # Over all pairs of words, call letterOverlaps
    overlaps = wordListLetterOverlaps(word_list)
    print("%d overlaps constructed"%(len(overlaps)))
    #print(overlaps)
    G = generateGraph(overlaps)
    print("Overlap graph constructed")
    # nx.draw_networkx(G);     plt.show()
    maximal_overlaps = ck_maximal_independent_set(G)
    print("%d overlaps in maximal independent"%(len(maximal_overlaps)))
    for i in sorted(maximal_overlaps):
        print(i)

    # iterate over all independent sets stemming from a maximal
    # independent set trying to find a feasible set
    feasible_overlaps = None
    layout = None
    for subset_size in range(len(maximal_overlaps),0,-1):                   # Largest to smallest subsets
        for subset in itertools.combinations(maximal_overlaps,subset_size): # All possible subsets of given size
            layout = construct_layout(word_list,subset)
            if layout != None:
                print("%d crossings in feasible layout"%subset_size)
                feasible_overlaps = subset
                break
        if feasible_overlaps != None:
            break
        
    if feasible_overlaps == None:
        print("No maximal sets could be realized :(")
    else:
        print("Feasible with crossings:")
        for o in feasible_overlaps:
            print(o)
        print(layout)
