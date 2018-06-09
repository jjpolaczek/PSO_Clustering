import cPickle as pickle
import os
from library import Book, Library
from clusterizer import PSO_Clusterizer, PSO_Result
import re
import numpy as np
import matplotlib.pyplot as plt
import operator
import readline
import random
import sys
class SimpleCompleter(object):

    def __init__(self, options):
        self.options = sorted(options)
        return

    def complete(self, text, state):
        response=None
        self.matches = None
        if state == 0:
            # This is the first time for this text, so build a match list.

            origline = readline.get_line_buffer()
            begin = readline.get_begidx()
            end = readline.get_endidx()
            being_completed = origline[begin:end]
            words = origline.split()

            if not origline:
                self.matches = self.options[:]
            else:
                self.matches = [s
                                for s in self.options
                                if s and s.startswith(origline)]
                self.matches = list(set(self.matches))

        #raw_output('Prompt ("stop" to quit): ')
        try:
            if len(self.matches) == 1:
                response = text+self.matches[0][len(origline):]
            else:
                print ""
                for match in self.matches:
                    print match
                sys.stdout.write("\nSelected> %s" % origline)
                response=None
        except IndexError:
            response = None
        return response


def checkFitness():
    resDict = {}
    resarray = np.zeros((len( os.listdir("PSO_results")),2))
    idx = 0
    for filename in os.listdir("PSO_results"):
        #with open(os.path.join("PSO_results", "PSO_result_c%d.pickle" % 25), 'wb') as f:
        with open(os.path.join("PSO_results",  filename), 'r') as f:
            result = pickle.load(f)
            resDict[filename] = result.fitness
            resarray[idx, 1] = int(re.findall("c\d+", filename)[0][1:])
            resarray[idx, 0] = result.fitness
            idx += 1
            print filename, result.fitness

    resarray.sort(axis=0)
    print resarray
    plt.plot(resarray[:,1], resarray[:,0])
    plt.title("Fitness vs cluster count")
    plt.xlabel("Cluster count")
    plt.ylabel("Fitness")
    #plt.show()
    # Selected 25 clusters for optimal clustering
class SuggestionSystem():
    def __init__(self, cluster_count):
        self.clusterCount = cluster_count
        loadSuccess = False
        with open(os.path.join("PSO_results",  "PSO_result_c%d.pickle" % self.clusterCount), 'r') as f:
            result = pickle.load(f)
            self.clusters = result.clusters
            self.labels = result.labels
            self.fitness = result.fitness
            print "Loaded %d clusters" % self.clusterCount
            loadSuccess = True
        if not loadSuccess:
            raise IOError("No file found for %d clusters" % self.clusterCount)
        loadSuccess = False
        #Now open the book database
        with open("vectorised2.pickle", 'rb') as f:
            obj = pickle.load(f)
            self.englishBooks, featureVector = obj
            print "Loaded %d books" % len(self.englishBooks)
            if len(self.englishBooks) != len(self.labels):
                raise IOError("Invalid clustering - label count different from book count")
            loadSuccess = True
        if not loadSuccess:
            raise IOError("No file found for library listing %s" % "vectorised2.pickle")

    def testDistribution(self):
        bags = []
        for i in range(self.clusterCount):
            bags.append({})
        for label, book in zip(self.labels, self.englishBooks):
            for subj in book.subject:
                try:
                    bags[label][subj] += 1
                except KeyError:
                    bags[label][subj] = 1

        sorted_subjects = []
        for i in range(self.clusterCount):
            bb = bags[i]
            sorted_subjects.append(sorted(bb.items(), key=operator.itemgetter(1)))
        if not os.path.exists("clusterDist"):
            os.mkdir("clusterDist")

        for i in range(len(sorted_subjects)):
            with open(os.path.join("clusterDist", "cluster%d.csv" % i), 'w') as f:
                f.write("sep=;" + os.linesep)
                for subj in reversed(sorted_subjects[i]):
                    f.write("%s;%d%s" %(subj[0], subj[1], os.linesep))
    def _setupCompleter(self):
        completeList = []
        for book in self.englishBooks:
            title = book.title.replace("\n", " ")
            completeList.append(title)
        readline.set_completer(SimpleCompleter(completeList).complete)
        readline.parse_and_bind('tab: complete')
        print "***************************************************"
        print "Welcome to book suggestion system!"
        print "Please choose a book you read from the library and"
        print "similar title suggestions will be returned!"

        print "Randomly chosen titles from our rich database:\n"
        i=0
        for title in random.sample(completeList, 5):
            if len(title) > 45:
                title= title[0:45] + "(...)"
            print "[%d] "%i + title
            i+=1
    def _findBook(self, name):
        for idx, book in enumerate(self.englishBooks):
            if name == book.title.replace("\n", " "):
                return idx
        return None

    def _findSuggestions(self, index):
        clusterNo = self.labels[index]

        members = []
        for idx, label in enumerate(self.labels):
            if label == clusterNo:
                members.append(idx)
        suggestion = random.sample(members, 15)

        for number, idx in enumerate(suggestion):
            print "\n****************SUGGESTION %d****************" % number
            print self.englishBooks[idx].description()

            #print self.englishBooks[idx].title.replace("\n", " ")
        return suggestion

    def mainLoop(self):
        self._setupCompleter()
        while True:
            line = raw_input('Enter book title ("exit" or "quit" to quit): ')
            if line == 'exit' or line == 'quit' or line =='q':
                break
            print 'ENTERED: "%s"' % line
            index = self._findBook(line)
            if index is not None:
                print self.englishBooks[index].description()
                print "Cluster %d" % self.labels[index]
            self._findSuggestions(index)


if __name__ == '__main__':
    iis = SuggestionSystem(20)
    iis.mainLoop()