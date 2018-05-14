import os
import pickle
from library import Book, Library
import logging
import sys
from time import time
from vectorizer import TextVectorizer
from clusterizer import PSO_Clusterizer

import numpy as np


logger = logging.getLogger(__name__)

#test on simpler data
def testSimple():
    clusters = np.zeros((100,3))
    for i in range(0,25,1):
        clusters[i,:] = np.array([1,1,1]) +  np.random.rand(1,3) * 0.1
    for i in range(25,50,1):
        clusters[i,:] = np.array([2,2,2]) +  np.random.rand(1,3) * 0.1
    for i in range(50,75,1):
        clusters[i,:] = np.array([3,3,3]) +  np.random.rand(1,3) * 0.1
    for i in range(75,100,1):
        clusters[i,:] = np.array([4,4,4]) +  np.random.rand(1,3) * 0.1

    result = PSO_Clusterizer.clusterize(clusters, no_clusters=4, t_max=100)
    print result

def testHard():
    html_dir_path="./books/indexes"
    library_listing_file="library_listing.pickle"
    nc=10
    with open("vectorised2.pickle", 'rb') as f:
        obj = pickle.load(f)
    englishBooks, featureVector = obj

    print type(featureVector)
    labels = PSO_Clusterizer.clusterize(featureVector, no_clusters=nc, t_max=10)
    print labels


    subjects = []
    for i in range(nc):
        print "\n\n\nXXXXXXXXXXXXXXXXXXXXXXXXXXx  LABEL %d\n" % i

        tmpset = {}
        for j in range(len(labels)):
            if labels[j] == i:
                for l in englishBooks[j].subject:
                    try:
                        tmpval = tmpset[l]
                        tmpset[l] = tmpval + 1
                    except KeyError:
                        tmpset[l] = 1
        subjects.append(tmpset)
        for key in tmpset:
            print "%s -- %d" % (key, tmpset[key])
    with open("result.txt", 'w') as f:
        for i in range(nc):
            f.write("\n\n\nXXXXXXXXXXXXXXXXXXXXXXXXXXx  LABEL %d\n" % i)
            for key in subjects[i]:
                f.write("%s -- %d\n" % (key, subjects[i][key]))

#testSimple()
testHard()