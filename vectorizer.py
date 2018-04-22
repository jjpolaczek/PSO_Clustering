import os
import pickle
from library import Book, Library
import logging
import sys
from time import time
from optparse import OptionParser


from sklearn.datasets import fetch_20newsgroups
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import Normalizer


logger = logging.getLogger(__name__)

class TextVectorizer():
    def __init__(self, bookList, opts):
        self.opts=opts
        self.bookList=bookList
        self.tmpVectorisedFile = "vectorised.pickle"

    def process(self):
        # Vectorizer settings
        logger.info("Extracting features from the training dataset using a sparse vectorizer")
        t0 = time()
        if self.opts.use_hashing:
            if self.opts.use_idf:
                # Perform an IDF normalization on the output of HashingVectorizer
                hasher = HashingVectorizer(n_features=self.opts.n_features,
                                           stop_words='english', alternate_sign=False,
                                           norm=None, binary=False)
                vectorizer = make_pipeline(hasher, TfidfTransformer())
            else:
                vectorizer = HashingVectorizer(n_features=self.opts.n_features,
                                               stop_words='english',
                                               alternate_sign=False, norm='l2',
                                               binary=False)
        else:
            vectorizer = TfidfVectorizer(max_df=0.5, max_features=self.opts.n_features,
                                         min_df=2, stop_words='english',
                                         use_idf=self.opts.use_idf)


        X = vectorizer.fit_transform(self.bookList[0:1000])
        logger.info("done in %fs", (time() - t0))
        logger.info("n_samples: %d, n_features: %d\n" % X.shape)
        if self.opts.n_components:
            logger.info("Performing dimensionality reduction using LSA")
            t0 = time()
            # Vectorizer results are normalized, which makes KMeans behave as
            # spherical k-means for better results. Since LSA/SVD results are
            # not normalized, we have to redo the normalization.
            svd = TruncatedSVD(self.opts.n_components)
            normalizer = Normalizer(copy=False)
            lsa = make_pipeline(svd, normalizer)

            X = lsa.fit_transform(X)

            logger.info("done in %fs", (time() - t0))

            explained_variance = svd.explained_variance_ratio_.sum()
            logger.info("Explained variance of the SVD step: %d\n", int(explained_variance * 100))

        vectorisedData = (self.bookList[0:1000], X)
        with open(self.tmpVectorisedFile, 'wb') as f:
            pickle.dump(vectorisedData, f, pickle.HIGHEST_PROTOCOL)

        logger.info("Extracted feature vector of %d dimensions, shape: %s", X.shape[1], X.shape)
        return vectorisedData
