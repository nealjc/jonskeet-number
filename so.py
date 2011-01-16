from lxml import etree
from sys import argv, exit
from math import ceil

"""
Calculates the 'Jon Skeet' number of Stack Overflow users
Parses the posts.xml file from the SO data dump,
builds a graph of co-authors, then does
a BFS from Jon Skeet to calculate everyone's number

"""

VERBOSE=False

class Answer:
    def __init__(self, id, userId, votes):
        self._id = id
        self._userId = userId
        self._votes = int(votes)

class QuestionParser:
    def __init__(self):
        self.questions = {}
    def start(self, tag, attrib):
        if tag == 'row' and not attrib.has_key("ClosedDate") and not attrib.has_key("CommunityOwnedDate"):
            if attrib["PostTypeId"] == '2' and attrib.has_key("OwnerUserId"):
                questionId = attrib["ParentId"]

                if self.questions.has_key(questionId):
                    self.questions[questionId][0].append(Answer(attrib["Id"], attrib["OwnerUserId"], attrib["Score"]))
            elif attrib["PostTypeId"] == '1':
                if attrib.has_key("AcceptedAnswerId"):
                    accepted = attrib["AcceptedAnswerId"]
                else:
                    accepted = None

                self.questions[attrib["Id"]] = ([], accepted)
            
    def end(self, tag):
        pass
    def data(self, data):
        pass
    def close(self):
        return self.questions


def updateGraph(graph, coAuthors):

    for author in coAuthors:
        if not graph.has_key(author):
            graph[author] = []

        for other in coAuthors:
            if other == author:
                continue

            if other not in graph[author]:
                graph[author].append(other)

def buildGraph(questions):
    totalCount = 0
    withCoCount= 0

    graph = {}
    
    for key in questions.keys():
        q = questions[key]
        
        if len(q[0]) == 0:
            continue
        
        q[0].sort(cmp=lambda x,y: y._votes - x._votes)

        if q[0][0]._votes < gamma:
            continue

        if VERBOSE:
            print "Question id %s has %d answers. Accepted: %s" % (key, len(q[0]), q[1])
            for a in q[0]:
                print "\tAnswer (%s) From user %s, score %d" % (a._id, a._userId, a._votes)

        max = q[0][0]._votes
        lowerLimit = ceil(max*alpha)


        coAuthors=[]
        for a in q[0]:
            if a._votes < lowerLimit:
                break
            coAuthors.append(a._userId)
            
        if VERBOSE:
            print "Co-authors are ", coAuthors

        totalCount += 1
        if len(coAuthors) > 1:
            withCoCount += 1
            updateGraph(graph, coAuthors)

        
    if VERBOSE:
        print "Authors: %d. With Co-authors: %d" % (totalCount, withCoCount)
    return graph


def BFS(adjList, center):
    if not adjList.has_key(center):
        print "Not a valid author", center
        exit(1)

    skeetNum = {}
    skeetNum[center] = 0
    visited = {}
    visited[center] = True
    current = 1

    queue = [center]
    while len(queue) > 0:
        next = queue[0]
        queue = queue[1:]

        found = False
        for node in adjList[next]:
            if node in visited.keys():
                continue

            found = True
            skeetNum[node] = current
            visited[node] = True
            queue.append(node)


        if found:
            current += 1

    return skeetNum
    
    

if __name__ == '__main__':

    if len(argv) != 5:
        print "Usage: python parse.py <file> <alpha> <gamma> <center>"
        exit(1)

    input = argv[1]
    #who to include for co-authors ([X*alpha, X], where X is highest scoring answer)
    alpha = float(argv[2])
    #which 'papers' are 'accepted' (need at least gamma upvotes for best answer)
    gamma = int(argv[3])
    #node to start BFS from
    center = argv[4]

    questions = etree.parse(input, etree.XMLParser(target=QuestionParser()))

    adjList = buildGraph(questions)
    skeetNumbers = BFS(adjList, center)
    for s in skeetNumbers:
        print s, skeetNumbers[s]


    
