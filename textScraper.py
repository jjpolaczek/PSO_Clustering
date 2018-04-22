import os
import pickle
from library import Book, Library
import logging
import sys
from time import time
from optparse import OptionParser

from vectorizer import TextVectorizer

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

    nc = 10
    ##Attempt Kmeans clustering
    if opts.minibatch:
        km = MiniBatchKMeans(n_clusters=nc, init='k-means++', n_init=1,
                             init_size=1000, batch_size=1000, verbose=opts.verbose)
    else:
        km = KMeans(n_clusters=nc, init='k-means++', max_iter=100, n_init=1,
                    verbose=opts.verbose)
    print("Clustering sparse data with %s" % km)
    t0 = time()
    labels = km.fit_predict(featureVector)
    print("done in %0.3fs" % (time() - t0))
    print(labels)
    for i in range(nc):
        print "LABEL %d" % i
        for j in range(len(labels)):
            if labels[j] == i:
                print englishBooks[j].subject




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
    op.add_option("--use-hashing",
                  action="store_true", default=True,
                  help="Use a hashing feature vectorizer")
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
