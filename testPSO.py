import os
import pickle
from library import Book, Library
import logging
import sys
from time import time
from vectorizer import TextVectorizer
from clusterizer import PSO_Clusterizer

import numpy as np
import time

import numpy as np
import matplotlib.pyplot as plt

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
    print "Test 2"
    clusters = np.zeros((100, 2))
    for i in range(0, 25, 1):
        clusters[i, :] = np.array([1, 1]) + np.random.rand(1, 2) * 0.6
    for i in range(25, 50, 1):
        clusters[i, :] = np.array([2, 2]) + np.random.rand(1, 2) * 0.6
    for i in range(50, 75, 1):
        clusters[i, :] = np.array([3, 3]) + np.random.rand(1, 2) * 0.6
    for i in range(75, 100, 1):
        clusters[i, :] = np.array([4, 4]) + np.random.rand(1, 2) * 0.6

    result = PSO_Clusterizer.clusterize(clusters, no_clusters=4, t_max=100, no_particles=1000)
    LABEL_COLOR_MAP = {0: 'r',
                       1: 'k',
                       2: 'g',
                       3: 'b'
    }

    label_color = [LABEL_COLOR_MAP[l] for l in result[0]]
    plt.scatter(clusters[:,0], clusters[:,1],c=label_color)
    plt.title("Clusters for synthetic data")
    plt.show()
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

def preCluster(min_c, max_c):
    points=max_c-min_c + 1
    html_dir_path="./books/indexes"
    library_listing_file="library_listing.pickle"
    with open("vectorised2.pickle", 'rb') as f:
        obj = pickle.load(f)
    englishBooks, featureVector = obj

    labels=np.zeros((points, featureVector.shape[0]))
    fitness=[]
    clusters=[]
    i=0
    for nc in range(min_c, max_c + 1, 1):
        print "Clustering for %d clusters" % nc
        labels[i,:], fit, clst= PSO_Clusterizer.clusterize(featureVector, no_clusters=nc, t_max=20)
        fitness.append((nc,float(fit)))
        clusters.append(clst)
        i += 1

    with open("clusteringPSO_labs.pickle", 'wb') as f:
        pickle.dump(labels, f, pickle.HIGHEST_PROTOCOL)
    with open("clusteringPSO_fitness.pickle", 'wb') as f:
        pickle.dump(fitness, f, pickle.HIGHEST_PROTOCOL)
    with open("clusteringPSO_clusters.pickle", 'wb') as f:
        pickle.dump(clusters, f, pickle.HIGHEST_PROTOCOL)

def testTmp():
    no_particles=50000
    no_clsters = 25
    no_dims = 50
    prevV = np.random.rand(no_particles, no_clsters, no_dims)
    gBest = np.random.rand(no_clsters, no_dims)
    pBest = np.random.rand(no_particles, no_clsters, no_dims)
    particles = np.random.rand(no_particles, no_clsters, no_dims)
    w = 0.9
    c1 = 0.5
    c2 = 0.7
    t0 = time.time()
    for i in xrange(no_particles):
        # Three components: 1: weight times previous velocity, 2: local optimum heuristic, 3: global optimum heuristic
        prevV[i, :, :] = w * prevV[i, :, :] + c1 * np.random.rand() * (
                    pBest[i, :, :] - particles[i, :, :]) + c2 * np.random.rand() * (gBest - particles[i, :, :])
        # print prevV[i, :, :]
        particles[i, :, :] += prevV[i, :, :]


    print "DT: ", time.time()-t0
testSimple()
#testHard()
#testTmp()
#preCluster(1,25)