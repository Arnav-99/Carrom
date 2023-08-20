#https://www.cs.cmu.edu/~112/notes/notes-data-and-operations.html

#different almostEqual definitions for different use-cases throughout code

def almostEqual(d1, d2):
    epsilon = 3
    return (abs(d2 - d1) < epsilon)

def almostEqual2(d1, d2):
    epsilon = 0.1
    return (abs(d2 - d1) < epsilon)

def almostEqual3(d1, d2):
    epsilon = 6
    return (abs(d2 - d1) < epsilon)

def almostEqual4(d1, d2):
    epsilon = 0.00000000001
    return (abs(d2 - d1) < epsilon)
