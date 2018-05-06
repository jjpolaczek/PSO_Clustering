import os
import pickle
from library import Book, Library
import logging
import sys
from time import time
from optparse import OptionParser
from vectorizer import TextVectorizer
from clusterizer import PSO_Clusterizer
from sklearn.cluster import KMeans, MiniBatchKMeans
#Topic: Clasterization of a large set of textual documents by means of a meta-heuristic Particle Swarm Optimization

logger = logging.getLogger(__name__)

html_dir_path="./books/indexes"
library_listing_file="library_listing.pickle"
op = OptionParser()

def main(opts):
    bookLib = Library(html_dir_path, False)
    englishBooks = bookLib.filterBooks("English", onlyWithSubject=True)
    logger.info("Processing %d books" % len(englishBooks))
    vectoriser = TextVectorizer(englishBooks, opts)

    englishBooks,featureVector = vectoriser.process()
    #englishBooks, featureVector = vectoriser.loadCheckpoint()
    nc = 100
    ##Attempt Kmeans clustering
    if opts.minibatch:
        km = MiniBatchKMeans(n_clusters=nc, init='k-means++', n_init=1,
                             init_size=1000, batch_size=1000, verbose=opts.verbose)
    else:
        km = KMeans(n_clusters=nc, init='k-means++', max_iter=100, n_init=1,
                    verbose=opts.verbose)
    logger.info("Clustering sparse data with %s" % km)
    t0 = time()
    labels = km.fit_predict(featureVector)
    logger.info("done in %0.3fs" % (time() - t0))
    #print(labels)
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




if __name__ == '__main__':
    #import logging.config
    logging.basicConfig(level=logging.INFO)
    #logging.config.fileConfig('/path/to/logging.conf')

    # parse commandline arguments
    op.add_option("--lsa",
                  dest="n_components", type="int", default=50,
                  help="Preprocess documents with latent semantic analysis.")
    op.add_option("--no-minibatch",
                  action="store_false", dest="minibatch", default=True,
                  help="Use ordinary k-means algorithm (in batch mode).")
    op.add_option("--no-idf",
                  action="store_false", dest="use_idf", default=True,
                  help="Disable Inverse Document Frequency feature weighting.")
    op.add_option("--n-features", type=int, default=10000,
                  help="Maximum number of features (dimensions)"
                       " to extract from text.")
    op.add_option("--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="Print progress reports inside k-means algorithm.")
    op.add_option("--reload-library",
                  action="store_true", dest="reload_lib", default=False,
                  help="Reload/Refresh and verify text file library if already pre-loaded")

    #argv = sys.argv[1:]
    (opts, args) = op.parse_args()

    main(opts)
