import os
import pickle
from library import Book, Library
import logging
import sys
from time import time
from vectorizer import TextVectorizer
from clusterizer import PSO_Clusterizer, PSO_Result

from optparse import OptionParser
from vectorizer import LSA_FILE_CHECKPOINT
import numpy as np
import time

import numpy as np


html_dir_path="./books/indexes"
library_listing_file="library_listing.pickle"
op = OptionParser()
logger = logging.getLogger(__name__)




def main(opts):
    html_dir_path="./books/indexes"
    library_listing_file="library_listing.pickle"

    with open(LSA_FILE_CHECKPOINT, 'rb') as f:
        obj = pickle.load(f)

    englishBooks, featureVector = obj

    labelsStore=[]
    fitnessStore=[]
    clustersStore=[]
    for retry in range(opts.no_retries):
        print "Clustering for %d clusters, attempt %d/%d" % (opts.no_clusters, retry+1, opts.no_retries)
        labels, fit, clst= PSO_Clusterizer.clusterize(featureVector, no_clusters=opts.no_clusters, t_max=20)
        labelsStore.append(labels)
        clustersStore.append(clst)
        fitnessStore.append(float(fit))

    bestidx=fitnessStore.index(min(fitnessStore))

    if not os.path.exists("PSO_results"):
        os.mkdir("PSO_results")



    retObj=PSO_Result(labelsStore[bestidx], fitnessStore[bestidx], clustersStore[bestidx])

    with open(os.path.join("PSO_results", "PSO_result_c%d.pickle" % opts.no_clusters), 'wb') as f:
        pickle.dump(retObj, f, pickle.HIGHEST_PROTOCOL)



if __name__ == '__main__':
    #import logging.config
    logging.basicConfig(level=logging.WARN)
    #logging.config.fileConfig('/path/to/logging.conf')

    # parse commandline arguments
    op.add_option("--clusters",
                  dest="no_clusters", type="int", default=5,
                  help="Number of clusters")
    op.add_option("--no-retries", type="int", dest="no_retries", default=1,
                  help="Number of retries of the clustering")

    op.add_option("--c_global", type="float", default=0.6,
                  help="Global PSO clustering coefficient")

    op.add_option("--c_local", type="float", default=0.6,
                  help="Local PSO clustering coefficient")

    op.add_option("--c_weight", type="float", default=0.6,
                  help="Particle weight coefficient")


    #argv = sys.argv[1:]
    (opts, args) = op.parse_args()

    main(opts)
