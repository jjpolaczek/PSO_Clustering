# Main imports
from sugSystem import SuggestionSystem
from library import Library
from vectorizer import TextVectorizer

#Python imports
import logging
import sys
from time import time
from optparse import OptionParser
from operator import itemgetter
from clusterizer import PSO_Clusterizer
import os

logger = logging.getLogger(__name__)

html_dir_path="./books/indexes"
library_listing_file="library_listing.pickle"
op = OptionParser()

def main(opts):
    # Check if need to reload the features and library
    if opts.reload_library or not SuggestionSystem.checkCheckpoint(opts.no_clusters):
        if opts.library_path is None or not Library.checkBookFolder(opts.library_path):
            logger.error("Cannot reload the library from %s, books not found, has the iso been mounted (mountdb.sh)?",opts.library_path)
        bookLib = Library(opts.library_path, opts.reload_library)
        englishBooks = bookLib.filterBooks("English", onlyWithSubject=True)
        logger.info("Processing %d books, vectorisation may take over 10 minutes" % len(englishBooks))
        vectoriser = TextVectorizer(englishBooks, opts)
        englishBooks, featureVector = vectoriser.process()

        if opts.no_clusters < 1:
            opts.no_clusters = 1
        labelsStore = []
        fitnessStore = []
        clustersStore = []
        logger.info("Clustering, may take over an hour for large cluster counts...")
        for retry in range(opts.cluster_retries):
            logger.info("Clustering for %d clusters, attempt %d/%d" % (opts.no_clusters, retry + 1, opts.cluster_retries))
            labels, fit, clst = PSO_Clusterizer.clusterize(featureVector, no_clusters=opts.no_clusters, t_max=20)
            labelsStore.append(labels)
            clustersStore.append(clst)
            fitnessStore.append(float(fit))

        bestResult = min(enumerate(fitnessStore), key=itemgetter(1))[0]
        PSO_Clusterizer.saveClustering(labelsStore[bestResult], fitnessStore[bestResult], clustersStore[bestResult])
        logger.info("Preprocessing complete for %d clusters" % opts.no_clusters)
    else:
        logger.info("Skipped initialization, checkpoint located, for data refresh use --reload_library argument")

    iis = SuggestionSystem(opts.no_clusters)
    iis.mainLoop()


if __name__ == '__main__':
    #import logging.config
    logging.basicConfig(level=logging.INFO)
    #logging.config.fileConfig('/path/to/logging.conf')

    # parse commandline arguments
    op.add_option("--lsa",dest="n_components", type="int", default=50,
                  help="Number of output dimensions for latent semantic analysis.")
    op.add_option("--no_clusters", type="int", default=20,
                  help="Number of clusters for the suggestion system")
    op.add_option("--library_path", type="string", default=None,
                  help="Path for text library")
    op.add_option("--n-features", type=int, default=10000,
                  help="Maximum number of features (dimensions)"
                       " to extract from text.")
    op.add_option("--cluster_retries", type="int", default=1,
                  help="Number of retries to attempt the clustering")
    op.add_option("--reload_library",
                  action="store_true", default=False,
                  help="Reload/Refresh and verify text file library if already pre-loaded")

    #argv = sys.argv[1:]
    (opts, args) = op.parse_args()

    main(opts)
