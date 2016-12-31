#!/usr/bin/python2
# -------------------------------------------------------------------
# dowlib.py
# -------------------------------------------------------------------
# purpose: tools for importing or generating double occurrence words
# -------------------------------------------------------------------
# author: Ryan Arredondo
# email: ryan.c.arredondo@gmail.com
# date: 6/2/2013
# -------------------------------------------------------------------
# updates:
#   12/31/2016 - Made PEP8 compliant - Ryan Arredondo
#   12/31/2016 - Made Python 3 compatible - Ryan Arredondo
# -------------------------------------------------------------------


def importDOWs(filename):
    """Given a file of dows, returns list of dows.
    """
    words = []
    with open(filename, "r") as myfile:
        for wordstr in myfile:
            dow = str2dow(wordstr[:-1])     # [:-1] to remove "\n" char
            words.append(dow)
            wordstr = myfile.readline()
    return words


def str2dow(wordstr):
    """Converts a str representing a dow with either no delimiters
    or delimited by commas into a list.
    """
    if "," in wordstr:
        w = wordstr.split(",")
    else:
        w = wordstr
    return relabel(w)


def dow2str(word):
    """Returns word as string, comma-delimited if word has label at least 10.
    """
    if len(word) < 20:
        word_str = "".join([str(a) for a in word])
    else:
        word_str = ",".join([str(a) for a in word])
    return word_str


def relabel(word):
    """Relabels word in canonical form beginning with one and incrementing
    the preceding labels by no more than 1.
    """
    code = []
    newword = list(word)
    for i in range(len(newword)):
        a = newword[i]
        if a in code:
            newword[i] = code.index(a)+1
        else:
            code.append(a)
            newword[i] = len(code)
    return newword


def isDOW(word):
    """Returns True if word is double occurrence word, else False."""
    return all(word.count(a) == 2 for a in set(word))


def getdows(n):
    """Constructs all double occurrence words of size n."""
    words = [[1, 1]]
    wordlen = 2*n
    currlen = 2
    while currlen != wordlen:
        currlen += 2
        newwords = []
        for word in words:
            temp_word = [a + 1 for a in word]
            temp_word.insert(0, 1)
            for i in range(1, currlen):
                newword = list(temp_word)
                newword.insert(i, 1)
                newwords.append(newword)
        words = newwords

    return words


def loopsaturate(word):
    """Returns the result of loop saturating word."""
    wordlen = len(word)
    wordcopy = list(word)
    for i in reversed(range(wordlen)):
        wordcopy.insert(i, wordlen+i)
        wordcopy.insert(i, wordlen+i)
    return relabel(wordcopy)


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 2:
        words = getdows(eval(sys.argv[1]))
        for word in words:
            print(dow2str(word))
