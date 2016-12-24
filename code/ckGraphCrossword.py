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

def checkFeasibility(listOfPairs):
    G = nx.Graph()
    for pair in listOfPairs:
        G.add_edge(pairFirstWord(pair), pairSecondWord(pair))
    try:
        nx.algorithms.bipartite.color(G)
        return True
    except nx.NetworkXError:
        return False

def ck_maximal_independent_set(G, nodes=None):
    """Return a random maximal independent set guaranteed to contain
    a given set of nodes.

    An independent set is a set of nodes such that the subgraph
    of G induced by these nodes contains no edges. A maximal
    independent set is an independent set such that it is not possible
    to add a new node and still get an independent set.
    
    Parameters
    ----------
    G : NetworkX graph 

    nodes : list or iterable
       Nodes that must be part of the independent set. This set of nodes
       must be independent.

    Returns
    -------
    indep_nodes : list 
       List of nodes that are part of a maximal independent set.

    Raises
    ------
    NetworkXUnfeasible
       If the nodes in the provided list are not part of the graph or
       do not form an independent set, an exception is raised.

    Examples
    --------
    >>> G = nx.path_graph(5)
    >>> nx.maximal_independent_set(G) # doctest: +SKIP
    [4, 0, 2]
    >>> nx.maximal_independent_set(G, [1]) # doctest: +SKIP
    [1, 3]
    
    Notes
    -----
    This algorithm does not solve the maximum independent set problem.

    """
    if not nodes:
        nodes = set([list(G.nodes())[0]])
    else:
        nodes = set(nodes)
    if not nodes.issubset(G):
        raise nx.NetworkXUnfeasible(
                "%s is not a subset of the nodes of G" % nodes)
    neighbors = set.union(*[set(G.neighbors(v)) for v in nodes])
    if set.intersection(neighbors, nodes):
        raise nx.NetworkXUnfeasible(
                "%s is not an independent set of G" % nodes)
    indep_nodes = list(nodes)
    available_nodes = set(G.nodes()).difference(neighbors.union(nodes))
    while available_nodes:
        node = list(available_nodes)[0]
        indep_nodes.append(node)
        available_nodes.difference_update(G.neighbors(node) + [node])
    return indep_nodes



if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("usage: python ckGraphCrossword.py wordList.txt")
        sys.exit(1)


    filename = sys.argv[1]
    wordList = []
    with open(filename) as f:
        wordList = f.read().splitlines()
    
    print("%d words read from %s" % (len(wordList),filename))

    # Over all pairs of words, call letterOverlaps
    overlaps = wordListLetterOverlaps(wordList)
    print("Overlaps constructed")
    #print(overlaps)
    G = generateGraph(overlaps)

    # nx.draw_networkx(G);     plt.show()

    print("Graph constructed")

    # iterate over all independent sets stemming from a maximal
    # independent set
    indList = ck_maximal_independent_set(G)

    for i in sorted(indList):
        print(i)

    for node in G.nodes():
        #print("Maximal independent set determined")
        feas = checkFeasibility(indList)
        if feas:
            print("Set can be realized!")
            print(indList)
            break
    if not feas:
        print("No maximal sets could be realized :(")
    #nx.draw_networkx(G)
    #plt.show()

    #print(letterOverlaps('deaf','dog'))
    #print(letterOverlaps('cringe','trifle'))
    #print(letterOverlaps('deaf','trifle'))
