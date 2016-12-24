import networkx as nx
import matplotlib.pyplot as plt
import random
import sys

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

if __name__ == '__main__':
    #with open('/Users/deronne/Downloads/linuxwords.txt') as f:
    #    wordList = []
    #    for line in f:
    #        if random.random() < 0.001:
    #            word = line.rstrip().lower()
    #            wordList.append(word)
    #print("Word list loaded: %d" %(len(wordList)))
    #print(wordList)

    # Just a random word list for now
    # wordList = ['accumulates', 'adele', 'alphabetical', 'bandages', 'brasses', 'brazes', 'breeches', 'brightness', 'deftly', 'duckling', 'flynn',
    #     'fricatives', 'galvin', 'ganymede', 'grounds', 'hymn', 'identification', 'inventory', 'kiss', 'languages', 'limerick', 'looming',
    #     'messiah', 'michaels', 'mustaches', 'prehistoric', 'prejudicial', 'punching']
    #wordList = wordList[0:20]
    wordList = ['deaf', 'dog', 'cringe', 'trifle', 'cat', 'lion', 'rind', 'paul', 'chris', 'kevin']
    
    # Over all pairs of words, call letterOverlaps
    overlaps = wordListLetterOverlaps(wordList)
    print("Overlaps constructed")
    #print(overlaps)
    G = generateGraph(overlaps)

    nx.draw_networkx(G);     plt.show()

    print("Graph constructed")
    for node in G.nodes():
        indList = nx.maximal_independent_set(G, [node])
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
