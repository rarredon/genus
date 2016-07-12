#!/usr/bin/python2
#-----------------
#dowlib.py
#-----------------
#purpose: tools for importing or generating double occurrence words
#-------------------------------------------------------------------
#author: Ryan Arredondo
#date: 6/2/2013
#-------------------------------------------------------------------

def importDOWs(filename):
    "given a file of dows, returns list of dows"
    words = []
    myfile = open(filename,"r")
    wordstr = myfile.readline()
    while wordstr != "":
        dow = str2dow(wordstr[:-1])     #[:-1] to remove "\n" character
        words.append(dow)
        wordstr = myfile.readline()
    return words

def str2dow(wordstr):
    """converts a str representing a dow with either no
    delimiters or delimited by commas into a list"""
    if "," in wordstr:
        w = wordstr.split(",")
    else:
        w = wordstr
    return relabel(w)

def dow2str(word):
    if len(word) < 20:
        word_str = "".join([str(a) for a in word])
    else:
        word_str = ",".join([str(a) for a in word])
    return word_str

def relabel(word):
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
    return all([word.count(a)==2 for a in set(word)])
               
def getdows(n):
    "constructs all double occurrence words of size n"
    words = [[1,1]]
    wordlen = 2*n
    currlen = 2
    while currlen != wordlen:
        currlen += 2
        newwords = []
        for word in words:
            temp_word = [a + 1 for a in word]
            temp_word.insert(0,1)
            for i in range(1,currlen):
                newword = list(temp_word)
                newword.insert(i,1)
                newwords.append(newword)
        words = newwords

    return words

def loopsaturate(word):
    wordlen = len(word)
    wordcopy = list(word)
    for i in reversed(range(wordlen)):
        wordcopy.insert(i,wordlen+i)
        wordcopy.insert(i,wordlen+i)
    return relabel(wordcopy)

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 2:
        words = getdows(eval(sys.argv[1]))
        for word in words:
            print dow2str(word)
