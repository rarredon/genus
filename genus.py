#!/usr/bin/python2
#------------------------------------------------------------------
#genus.py
#------------------------------------------------------------------
#purpose: to compute the genus range of double occurrence words
#------------------------------------------------------------------
#usage: 1) genus.py w1 [w2 w3 ...]
#   where w1 is non-delimited or comma-delimited dow
#       2) genus.py -t dows1.txt [dows2.txt dows3.txt ...]
#   where dows1.txt is a text file in which each line is dow
#   of the format specified for w1 above
#       3) use optional argument "-r" to print range rather than
#   spectrum
#       4) use optional argument '-v' to print verbosely
#   the genus for every connection
#       5) use optional argument '-e' to consider assembly graphs
#   with endpoints
#------------------------------------------------------------------
#author: Ryan Arredondo
#date: 6/2/2013
#------------------------------------------------------------------
#updated: 8/18/2013
#------------------------------------------------------------------

import sys, itertools
from dowlib import *

def main(argv):
    printrange = False
    verbose = False
    hasEndpoints = False
    if "-r" in argv:
        printrange = True
        argv.pop(argv.index("-r"))
    if "-v" in argv:
        verbose = True
        argv.pop(argv.index("-v"))
    if "-e" in argv:
        hasEndpoints = True
        argv.pop(argv.index("-e"))
        
    if len(argv) == 1 or "-h" in argv:
        print_usage()
        return
    elif argv[1] == "-t":
        for filename in argv[2:]:
            words = importDOWs(filename)
            for word in words:
                if isDOW(word):
                    if printrange:
                        print "%s: %s" % (dow2str(word), \
                            list(set(getGenera(word,hasEndpoints,verbose))))
                    else:
                        print "%s: %s" % (dow2str(word), \
                            show(getGenera(word,hasEndpoints,verbose)))
                else:
                    print "%s: not dow" % dow2str(word)
    else:
        for wordstr in argv[1:]:
            word = str2dow(wordstr)
            if isDOW(word):
                if printrange:
                    print "%s: %s" % (dow2str(word), \
                        list(set(getGenera(word,hasEndpoints,verbose))))
                else:
                    print "%s: %s" % (dow2str(word), \
                        show(getGenera(word,hasEndpoints,verbose)))
            else:
                print "%s: not dow" % wordstr


def print_usage():
    """description of how the program should be used"""
    print "usage: 1) genus.py w1 [w2 w3 ...]"
    print "   where w1 is non-delimited or comma-delimited dow"
    print "       2) genus.py -t dows1.txt [dows2.txt dows3.txt ...]"
    print "   where dows1.txt is a text file in which each line is dow"
    print "   of the format specified for w1 above"
    print "       3) use optional argument '-r' to print range rather"
    print "   than spectrum"
    print "       4) use optional argument '-v' to print verbosely"
    print "   the genus for every connection"
    print "       5) use optional argument '-e' to consider assembly graphs"
    print "   with endpoints"
    
def show(genera):
    """takes the output of getGenera and presents it so that the
    counts of the genera are shown"""
    if type(genera[0]) == list:
        if len(genera[0]) == 0:
            counts = [[],[0]*(max(genera[1])+1)]
        elif len(genera[1]) == 0:
            counts = [[0]*(max(genera[0])+1),[]]
        else:
            counts = [[0]*(max(genera[0])+1),[0]*(max(genera[1])+1)]
        for i in range(2):
            for g in genera[i]:
                counts[i][g] += 1
        return [[(g,counts[i][g]) for g in set(genera[i])] for i in range(2)]
    else:
        counts = [0]*(max(genera)+1)
        for g in genera:
            counts[g] += 1
        return [(g,counts[g]) for g in set(genera)]


def getGenera(w,hasEndpoints,verbose):
    """returns list of all genera for all possible connections of
    graph with corresponding edges E and cyclical arrangement Arr"""
    E = getEdges(w)
    Arr = getCyclicArrangement(E)
    if hasEndpoints:
        genera = [[],[]]
    else:
        genera = []
    numberOfVertices = len(set(flatten(E)))
    
    for connection in itertools.product(range(2),repeat=numberOfVertices):
        BSet = getBoundaries(E,Arr,connection)
        numberOfBoundaries = len(BSet)
        genus = (numberOfVertices - numberOfBoundaries + 2)/2
        if not hasEndpoints:
            genera.append(genus)
        elif 2 in [count(B,E[-1]) for B in BSet]:
            genera[0].append(genus)
        else:
            genera[1].append(genus)
            
        if verbose:
            print "%s: %d" % (connection,genus)

    return genera

def getBoundaries(E,Arr,connection):
    """returns list of lists of edges in which each list represents
    a boundary component of graph with connections described by connection,
    edges E and cyclical arrangement of edges Arr"""
    #Boundary set is initialized with loops since a loop
    #+  will always form its own boundary regardless of connection
    BSet = [[e] for e in E if e[0] == e[1]]

    #DirSet holds the directions in which an edge is being traced
    #Used by function tracedOnRightOnly
    DirSet = [e[0] for e in flatten(BSet)]

    #for readability, returns True if connection is flipped or False o.w.
    flipped = lambda val: bool(val)
    
    #Constructs all boundaries by taking a "left" at each vertex
    #TODO:test if loop-nested word gives an issue
    edgesNotTracedOnLeft = map(lambda e: notTracedOnLeft(e,BSet,DirSet), E)
    while any(edgesNotTracedOnLeft):
        e1 = E[edgesNotTracedOnLeft.index(True)]
        B = [e1]
        towards = e1[1]
        DirSet.append(towards)
        
        #if connection is flipped, we turn right (o.w., turn left) at
        #   vertex=towards
        if flipped(connection[towards - 1]):
            e, towards = turnRight(e1,towards, Arr)
        else:
            e, towards = turnLeft(e1,towards, Arr)
        
        #repeat until we get back to starting edge in same direction
        while e1 is not e or e1[1] != towards:
            B.append(e)
            DirSet.append(towards)
            
            if flipped(connection[towards - 1]):
                e, towards = turnRight(e,towards,Arr)
            else:
                e, towards = turnLeft(e,towards,Arr)
        BSet.append(B)
        edgesNotTracedOnLeft =  \
            map(lambda e: notTracedOnLeft(e,BSet,DirSet), E)

    #Constructs all boundaries by taking a "right" at each vertex
    edgesNotTracedOnRight = map(lambda e: count(flatten(BSet),e) != 2, E)
    while any(edgesNotTracedOnRight):
        e1 = E[edgesNotTracedOnRight.index(True)]
        B = [e1]
        towards = e1[1]
        
        #if connection is flipped, we turn left (o.w., turn right) at
        #   vertex=towards
        if flipped(connection[towards - 1]):
            e, towards = turnLeft(e1,towards, Arr)
        else:
            e, towards = turnRight(e1,towards, Arr)
        
        #repeat until we get back to starting edge in same direction
        while e1 is not e or e1[1] != towards:
            B.append(e)
            if flipped(connection[towards - 1]):
                e, towards = turnLeft(e,towards,Arr)
            else:
                e, towards = turnRight(e,towards,Arr)
        BSet.append(B)
        edgesNotTracedOnRight = map(lambda e: count(flatten(BSet),e) != 2, E)

    return BSet

def notTracedOnLeft(e,BSet,Directions):
    "determines whether an edge e has NOT been traced on the left"
    FlatBSet = list(flatten(BSet))
    c = count(FlatBSet,e)
    if c == 0: return True
    elif c == 2: return False
    else:
    #check if edge is traced on right only
        for i in range(len(FlatBSet)):
            if FlatBSet[i] is e:
                ind = i
        return Directions[ind] == e[0]

def turnLeft(e,towards,Arr):
    """given graphs cylical arrangement Arr we turn "left" from
    edge e towards vertex=towards and return new edge and vertex towards
    """
    for i in range(4):
        if Arr[towards-1][i] is e and Arr[towards-1][(i+1)%4] is not e:
            ind = i
    nextEdge = Arr[towards-1][(ind+1)%4]
    if towards != nextEdge[0]:
        return nextEdge, nextEdge[0]
    else:
        return nextEdge, nextEdge[1]

def turnRight(e,towards,Arr):    
    """given graphs cylical arrangement Arr we turn "right" from
    edge e towards vertex=towards and return new edge and vertex towards
    """
    for i in range(4):
        if Arr[towards-1][i] is e and Arr[towards-1][i-1] is not e:
            ind = i
    nextEdge = Arr[towards-1][ind-1]
    if towards != nextEdge[0]:
        return nextEdge, nextEdge[0]
    else:
        return nextEdge, nextEdge[1]

def getCyclicArrangement(E):
    "returns list of edges as they appear cyclically around each vertex"
    Arr = [[] for _ in set(flatten(E))]
    for e in E:
        Arr[e[0]-1].append(e)
    for e in E:
        Arr[e[1]-1].append(e)
    #following edges must be swapped for proper cyclic arrangement
    Arr[0][2],Arr[0][3] = Arr[0][3],Arr[0][2]
    return Arr

def getEdges(w):
    "returns edges (pairs of vertices) of assembly graph corresponding to w"
    w2 = 2*w
    return [w2[i:i+2] for i in range(len(w))]

def count(listOflists,myList):
    "counts occurrence of myList in listOflists by reference, not value"
    return sum(1 and int(myList is l) for l in listOflists)

def flatten(listOflists):
    "removes outtermost pairs of braces in a nested list"
    return itertools.chain.from_iterable(listOflists)


if __name__ == "__main__":
    main(sys.argv)
